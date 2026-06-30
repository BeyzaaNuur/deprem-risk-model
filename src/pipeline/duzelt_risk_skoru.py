import pandas as pd
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
OUT_DIR  = os.path.join(BASE_DIR, "data", "processed")

# ─────────────────────────────────────────────
# İl adı düzeltme sözlüğü
# Arkadaşının dosyasındaki hatalı/eksik karakterli isimler → doğru isimler
# ─────────────────────────────────────────────
IL_DUZELTME = {
    "Mugla": "Muğla",
    "K. Maras": "Kahramanmaraş",
    "Izmir": "İzmir",
    "Afyon": "Afyonkarahisar",
    "Adiyaman": "Adıyaman",
    "Çankiri": "Çankırı",
    "Aydin": "Aydın",
    "Diyarbakir": "Diyarbakır",
    "Tekirdag": "Tekirdağ",
    "Balikesir": "Balıkesir",
    "Sirnak": "Şırnak",
    "Sanliurfa": "Şanlıurfa",
    "Agri": "Ağrı",
    "Mus": "Muş",
    "Kirsehir": "Kırşehir",
    "Istanbul": "İstanbul",
    "Kinkkale": "Kırıkkale",
    "Zinguldak": "Zonguldak",
    "Nigde": "Niğde",
    "Eskisehir": "Eskişehir",
    "Kirklareli": "Kırklareli",
    "Gümüshane": "Gümüşhane",
}

def yukle():
    print("[1/4] Dosyalar yükleniyor...")
    risk_yol = os.path.join(OUT_DIR, "il_risk_skoru.csv")
    maruziyet_yol = os.path.join(OUT_DIR, "maruziyet_skoru.csv")
    dask_yol = os.path.join(OUT_DIR, "dask_sigortacilik.csv")

    df_risk = pd.read_csv(risk_yol)
    df_maruziyet = pd.read_csv(maruziyet_yol)
    df_dask = pd.read_csv(dask_yol)

    print(f"    il_risk_skoru.csv     : {len(df_risk)} satır")
    print(f"    maruziyet_skoru.csv   : {len(df_maruziyet)} satır")
    print(f"    dask_sigortacilik.csv : {len(df_dask)} satır")
    return df_risk, df_maruziyet, df_dask

def il_isimlerini_duzelt(df, sutun="il"):
    """İl adlarını sözlükten düzeltir, baş/son boşlukları temizler."""
    df[sutun] = df[sutun].str.strip()
    df[sutun] = df[sutun].replace(IL_DUZELTME)
    return df

def eksikleri_kontrol_et(df_risk, df_maruziyet):
    """Hangi iller maruziyet verisinde eksik, hangileri fazladan var."""
    print("\n[2/4] Eksik il kontrolü yapılıyor...")
    risk_iller = set(df_risk["il"])
    maruziyet_iller = set(df_maruziyet["il"])

    sadece_riskte = risk_iller - maruziyet_iller
    sadece_maruziyette = maruziyet_iller - risk_iller

    if sadece_riskte:
        print(f"    Risk dosyasında olup maruziyette OLMAYAN iller ({len(sadece_riskte)}):")
        print(f"    {sorted(sadece_riskte)}")
    if sadece_maruziyette:
        print(f"    Maruziyette olup risk dosyasında OLMAYAN iller ({len(sadece_maruziyette)}):")
        print(f"    {sorted(sadece_maruziyette)}")
    if not sadece_riskte and not sadece_maruziyette:
        print("    Tüm iller eşleşiyor ✓")

def yeniden_birlestir(df_risk, df_maruziyet, df_dask):
    """İsim düzeltmesi sonrası NA'ları yeniden hesapla."""
    print("\n[3/4] Veriler yeniden birleştiriliyor...")

    # Sadece sismik + DASK sabit kalan sütunları al, maruziyet'i temizden çek
    df_birlesik = df_risk[["il", "sismik_tehlike", "sigortasizlik_acigi"]].copy()

    # Maruziyet ve kırılganlığı doğru kaynaktan çek
    df_birlesik = df_birlesik.merge(
        df_maruziyet[["il", "nufus_skoru", "kirilganlik_skoru", "maruziyet_skoru"]],
        on="il", how="left"
    )

    # Hâlâ eşleşmeyen var mı kontrol et
    eksik = df_birlesik[df_birlesik["maruziyet_skoru"].isna()]
    if not eksik.empty:
        print(f"    Uyarı: {len(eksik)} il hâlâ eşleşmedi: {list(eksik['il'])}")
        print("    Bu iller için Türkiye ortalaması atanacak.")
        ort_maruziyet = df_birlesik["maruziyet_skoru"].mean()
        ort_kirilganlik = df_birlesik["kirilganlik_skoru"].mean()
        df_birlesik["maruziyet_skoru"] = df_birlesik["maruziyet_skoru"].fillna(ort_maruziyet)
        df_birlesik["kirilganlik_skoru"] = df_birlesik["kirilganlik_skoru"].fillna(ort_kirilganlik)

    # Bileşik risk skorunu fizibilite raporundaki ağırlıklarla yeniden hesapla
    # Sismik %40, Maruziyet %30, Kırılganlık %20, Sigortasızlık %10
    df_birlesik["bilesik_risk_skoru"] = (
        df_birlesik["sismik_tehlike"] * 0.40 +
        df_birlesik["maruziyet_skoru"] * 0.30 +
        df_birlesik["kirilganlik_skoru"] * 0.20 +
        df_birlesik["sigortasizlik_acigi"] * 0.10
    ).round(3)

    df_birlesik = df_birlesik.sort_values("bilesik_risk_skoru", ascending=False).reset_index(drop=True)
    return df_birlesik

def kaydet_ve_raporla(df):
    print("\n[4/4] Sonuç kaydediliyor...")
    yol = os.path.join(OUT_DIR, "il_risk_skoru_duzeltilmis.csv")
    df.to_csv(yol, index=False, encoding="utf-8-sig")
    print(f"    Kaydedildi: {yol} ✓")

    print("\n=== EN RİSKLİ 10 İL (Düzeltilmiş) ===")
    print(df[["il", "sismik_tehlike", "maruziyet_skoru", "kirilganlik_skoru", "bilesik_risk_skoru"]].head(10).to_string(index=False))

    na_sayisi = df["bilesik_risk_skoru"].isna().sum()
    print(f"\nKalan NA sayısı: {na_sayisi}")
    print(f"Toplam il sayısı: {len(df)}")

def main():
    print("İL RİSK SKORU — TÜRKÇE KARAKTER & EŞLEŞME DÜZELTMESİ")
    print("="*55)

    df_risk, df_maruziyet, df_dask = yukle()

    # İsim düzeltmesi
    df_risk = il_isimlerini_duzelt(df_risk)
    df_maruziyet = il_isimlerini_duzelt(df_maruziyet, sutun="il")
    df_dask = il_isimlerini_duzelt(df_dask, sutun="il")

    eksikleri_kontrol_et(df_risk, df_maruziyet)
    df_sonuc = yeniden_birlestir(df_risk, df_maruziyet, df_dask)
    kaydet_ve_raporla(df_sonuc)

    print("\nDüzeltme tamamlandı.")
    print("Dosya: data/processed/il_risk_skoru_duzeltilmis.csv")
    print("Bu dosyayı Power BI'a aktaracağız.")

if __name__ == "__main__":
    main()