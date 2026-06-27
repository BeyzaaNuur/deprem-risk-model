import requests
import pandas as pd
from datetime import datetime
import time
import os

# Çıktı klasörü
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# AFAD API — Kandilli yedekli
AFAD_URL = "https://deprem.afad.gov.tr/apiv2/event/filter"
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

def fetch_afad(start="1990-01-01", end="2024-12-31", min_mag=4.0):
    """AFAD API'den deprem verisi çeker."""
    print(f"AFAD'dan veri çekiliyor ({start} → {end}, M≥{min_mag})...")
    params = {
        "start": start,
        "end": end,
        "minmag": min_mag,
        "maxmag": 10.0,
        "minlat": 35.0,
        "maxlat": 43.0,
        "minlon": 25.0,
        "maxlon": 45.0,
        "format": "json",
        "limit": 10000,
        "offset": 1,
        "orderby": "timedesc"
    }
    try:
        r = requests.get(AFAD_URL, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        if not data:
            print("AFAD boş yanıt döndü.")
            return None
        df = pd.DataFrame(data)
        print(f"AFAD: {len(df)} kayıt alındı.")
        return df
    except Exception as e:
        print(f"AFAD hatası: {e}")
        return None

def fetch_usgs(start="1990-01-01", end="2024-12-31", min_mag=4.0):
    """USGS API'den Türkiye deprem verisi çeker (AFAD yedeği)."""
    print(f"USGS'den veri çekiliyor ({start} → {end}, M≥{min_mag})...")
    params = {
        "format": "geojson",
        "starttime": start,
        "endtime": end,
        "minmagnitude": min_mag,
        "minlatitude": 35.0,
        "maxlatitude": 43.0,
        "minlongitude": 25.0,
        "maxlongitude": 45.0,
        "limit": 20000,
        "orderby": "time"
    }
    try:
        r = requests.get(USGS_URL, params=params, timeout=60)
        r.raise_for_status()
        geojson = r.json()
        features = geojson.get("features", [])
        if not features:
            print("USGS boş yanıt döndü.")
            return None

        rows = []
        for f in features:
            props = f["properties"]
            coords = f["geometry"]["coordinates"]
            rows.append({
                "tarih": datetime.utcfromtimestamp(props["time"] / 1000).strftime("%Y-%m-%d %H:%M:%S"),
                "buyukluk": props.get("mag"),
                "derinlik_km": coords[2],
                "enlem": coords[1],
                "boylam": coords[0],
                "yer": props.get("place", ""),
                "kaynak": "USGS"
            })

        df = pd.DataFrame(rows)
        print(f"USGS: {len(df)} kayıt alındı.")
        return df
    except Exception as e:
        print(f"USGS hatası: {e}")
        return None

def temizle_afad(df):
    df.columns = df.columns.str.strip().str.lower()
    df.columns = df.columns.str.replace(r'\(.*\)', '', regex=True).str.strip()
    
    rename_rehberi = {}
    for sutun in df.columns:
        if sutun in ['tarih', 'tarih_ts', 'date', 'zaman']:
            rename_rehberi[sutun] = 'tarih'
        elif sutun in ['büyüklük', 'buyukluk', 'mag', 'magnitude']:
            rename_rehberi[sutun] = 'buyukluk'
        elif sutun in ['derinlik', 'derinlik_km', 'depth']:
            rename_rehberi[sutun] = 'derinlik_km'
            
    df = df.rename(columns=rename_rehberi)
    
    if 'kaynak' not in df.columns:
        df['kaynak'] = 'AFAD'
        
    hedef_sutunlar = ["tarih", "buyukluk", "derinlik_km", "enlem", "boylam", "yer", "kaynak"]
    mevcut_hedefler = [sutun for sutun in hedef_sutunlar if sutun in df.columns]
    
    return df[mevcut_hedefler]

    return df[["tarih", "buyukluk", "derinlik_km", "enlem", "boylam", "yer", "kaynak"]]

def kalite_kontrol(df):
    """Temel veri kalite kontrolleri."""
    print("\n--- Veri Kalite Raporu ---")
    print(f"Toplam kayıt     : {len(df)}")
    print(f"Eksik değerler   :\n{df.isnull().sum()}")
    print(f"Büyüklük aralığı : {df['buyukluk'].min():.1f} — {df['buyukluk'].max():.1f}")
    print(f"Derinlik aralığı : {df['derinlik_km'].min():.1f} — {df['derinlik_km'].max():.1f} km")
    print(f"Tarih aralığı    : {df['tarih'].min()} → {df['tarih'].max()}")

    # Aykırı değer tespiti
    derin_anomali = df[df["derinlik_km"] > 700]
    if not derin_anomali.empty:
        print(f"Uyarı: {len(derin_anomali)} kayıt 700km+ derinlikte (kontrol et)")

    mag_anomali = df[df["buyukluk"] > 9.5]
    if not mag_anomali.empty:
        print(f"Uyarı: {len(mag_anomali)} kayıt M9.5+ (kontrol et)")

    print("--------------------------\n")

def kaydet(df, dosya_adi):
    """Veriyi CSV olarak kaydeder."""
    yol = os.path.join(OUTPUT_DIR, dosya_adi)
    df.to_csv(yol, index=False, encoding="utf-8-sig")
    print(f"Kaydedildi: {yol}")
    return yol

def main():
    START = "1990-01-01"
    END   = "2024-12-31"
    MAG   = 4.0

    # 1. AFAD'dan çek
    df_afad = fetch_afad(start=START, end=END, min_mag=MAG)

    if df_afad is not None and not df_afad.empty:
        df_afad = temizle_afad(df_afad)
        kaydet(df_afad, "afad_depremler_ham.csv")
    else:
        print("AFAD başarısız, USGS yedek kaynağa geçiliyor...")
        df_afad = None

    # Kısa bekleme (API礼儀)
    time.sleep(2)

    # 2. USGS'den çek (her zaman — doğrulama için)
    df_usgs = fetch_usgs(start=START, end=END, min_mag=MAG)
    if df_usgs is not None and not df_usgs.empty:
        kaydet(df_usgs, "usgs_depremler_ham.csv")

    # 3. Birleştir (AFAD öncelikli, USGS yedek)
    kaynaklist = [df for df in [df_afad, df_usgs] if df is not None]
    if not kaynaklist:
        print("Hata: Her iki kaynaktan da veri alınamadı.")
        return

    df_birlesik = pd.concat(kaynaklist, ignore_index=True)

    # Tarih sütununu string'e çevir (sort için)
    df_birlesik["tarih"] = df_birlesik["tarih"].astype(str)
    df_birlesik = df_birlesik.sort_values("tarih").reset_index(drop=True)

    # Eksik değerleri düşür
    df_birlesik = df_birlesik.dropna(subset=["buyukluk", "enlem", "boylam"])

    # Kalite raporu
    kalite_kontrol(df_birlesik)

    # Kaydet
    kaydet(df_birlesik, "depremler_birlesik.csv")
    print(f"\nTamamlandı. {len(df_birlesik)} deprem kaydı hazır.")

if __name__ == "__main__":
    main()
