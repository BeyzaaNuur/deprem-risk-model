import pandas as pd
import os
import re

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
OUT_DIR  = os.path.join(BASE_DIR, "data", "processed")

def yukle():
    print("[1/5] Ham AFAD verisi yükleniyor...")
    yol = os.path.join(RAW_DIR, "afad_depremler_detayli.csv")
    df = pd.read_csv(yol, encoding="utf-8")
    df.columns = [c.strip() for c in df.columns]
    print(f"    {len(df)} satır yüklendi")
    print(f"    Sütunlar: {list(df.columns)}")
    return df

def temizle(df):
    print("\n[2/5] Veri temizleniyor...")

    df_temiz = pd.DataFrame()
    df_temiz["tarih"] = pd.to_datetime(
        df["Olus tarihi"].astype(str) + " " + df["Olus zamani"].astype(str),
        errors="coerce"
    )
    df_temiz["enlem"] = pd.to_numeric(df["Enlem"], errors="coerce")
    df_temiz["boylam"] = pd.to_numeric(df["Boylam"], errors="coerce")
    df_temiz["derinlik_km"] = pd.to_numeric(df["Der(km)"], errors="coerce")

    # Büyüklük: Mw varsa onu kullan, yoksa ML, yoksa xM
    df_temiz["buyukluk"] = pd.to_numeric(df["Mw"], errors="coerce")
    df_temiz["buyukluk"] = df_temiz["buyukluk"].fillna(pd.to_numeric(df["ML"], errors="coerce"))
    df_temiz["buyukluk"] = df_temiz["buyukluk"].fillna(pd.to_numeric(df["xM"], errors="coerce"))

    df_temiz["yer"] = df["Yer"].astype(str)
    df_temiz["kaynak"] = "AFAD_detayli"

    # Geçersiz satırları at
    once = len(df_temiz)
    df_temiz = df_temiz.dropna(subset=["tarih", "enlem", "boylam", "buyukluk"])
    df_temiz = df_temiz[(df_temiz["buyukluk"] > 0) & (df_temiz["buyukluk"] < 10)]
    sonra = len(df_temiz)
    print(f"    {once - sonra} geçersiz satır temizlendi")
    print(f"    Kalan: {sonra} kayıt")

    return df_temiz

def il_cikar(df):
    """Yer sütunundan il adını parantez içinden çıkarır."""
    print("\n[3/5] İl adı çıkarılıyor (Yer sütunundan)...")

    def il_bul(yer_metni):
        match = re.search(r"\(([^)]+)\)", str(yer_metni))
        if match:
            return match.group(1).strip().title()
        return None

    df["il_ham"] = df["yer"].apply(il_bul)

    # Türkçe karakter düzeltmesi (AFAD'ın büyük harf + karaktersiz yazımı)
    il_map = {
        "Kahramanmaras": "Kahramanmaraş", "Adiyaman": "Adıyaman",
        "Sanliurfa": "Şanlıurfa", "Mugla": "Muğla", "Izmir": "İzmir",
        "Nigde": "Niğde", "Cankiri": "Çankırı", "Diyarbakir": "Diyarbakır",
        "Tekirdag": "Tekirdağ", "Balikesir": "Balıkesir", "Sirnak": "Şırnak",
        "Agri": "Ağrı", "Mus": "Muş", "Kirsehir": "Kırşehir",
        "Istanbul": "İstanbul", "Kirikkale": "Kırıkkale", "Zonguldak": "Zonguldak",
        "Eskisehir": "Eskişehir", "Kirklareli": "Kırklareli", "Gumushane": "Gümüşhane",
        "Bingol": "Bingöl", "Elazig": "Elazığ", "Usak": "Uşak",
        "Canakkale": "Çanakkale", "Aydin": "Aydın", "Corum": "Çorum",
        "Bitlis": "Bitlis", "Edirne Karadeniz": "Edirne",
    }
    df["il"] = df["il_ham"].replace(il_map)

    eslesen = df["il"].notna().sum()
    print(f"    {eslesen}/{len(df)} kayıt için il tespit edildi ({eslesen/len(df)*100:.1f}%)")

    return df

def kaydet(df):
    print("\n[4/5] Temizlenmiş veri kaydediliyor...")
    yol = os.path.join(RAW_DIR, "afad_depremler_temiz_detayli.csv")
    df.to_csv(yol, index=False, encoding="utf-8-sig")
    print(f"    Kaydedildi: {yol} ✓")
    return yol

def il_bazinda_yeni_istatistik(df):
    print("\n[5/5] İl bazında yeni sismik istatistik hesaplanıyor...")

    df_il = df.dropna(subset=["il"])

    istatistik = df_il.groupby("il").agg(
        deprem_sayisi = ("buyukluk", "count"),
        ort_buyukluk  = ("buyukluk", "mean"),
        max_buyukluk  = ("buyukluk", "max"),
        ort_derinlik  = ("derinlik_km", "mean"),
        m4_ustu       = ("buyukluk", lambda x: (x >= 4.0).sum()),
        m5_ustu       = ("buyukluk", lambda x: (x >= 5.0).sum()),
        m6_ustu       = ("buyukluk", lambda x: (x >= 6.0).sum()),
    ).reset_index()

    istatistik["sismik_skor"] = (
        istatistik["deprem_sayisi"] / istatistik["deprem_sayisi"].max() * 5 +
        istatistik["max_buyukluk"]  / istatistik["max_buyukluk"].max()  * 3 +
        istatistik["m5_ustu"]       / max(istatistik["m5_ustu"].max(), 1) * 2
    ).round(2)

    istatistik = istatistik.sort_values("sismik_skor", ascending=False).reset_index(drop=True)

    yol = os.path.join(OUT_DIR, "il_sismik_istatistik_v2.csv")
    istatistik.to_csv(yol, index=False, encoding="utf-8-sig")

    print(f"    {len(istatistik)} il için istatistik hesaplandı")
    print(f"    Kaydedildi: {yol} ✓")
    print("\n    === EN RİSKLİ 15 İL (Genişletilmiş Veri) ===")
    print(istatistik[["il", "deprem_sayisi", "max_buyukluk", "m6_ustu", "sismik_skor"]].head(15).to_string(index=False))

def main():
    print("AFAD DETAYLI VERİ — TEMİZLEME VE İL EŞLEŞTİRME")
    print("="*55)

    df = yukle()
    df_temiz = temizle(df)
    df_il = il_cikar(df_temiz)
    kaydet(df_il)
    il_bazinda_yeni_istatistik(df_il)

    print("\nTamamlandı.")
    print("Yeni dosya: data/processed/il_sismik_istatistik_v2.csv")
    print("Bu dosya eski il_sismik_istatistik.csv'den daha kapsamlı (50.000 kayıt).")

if __name__ == "__main__":
    main()
