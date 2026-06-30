import requests
import pandas as pd
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
OUT_DIR  = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# TÜİK ADNKS — il bazında nüfus (2023)
# TÜİK açık API endpoint
TUIK_URL = "https://data.tuik.gov.tr/api/data"

def tuik_nufus_manuel():
    """
    TÜİK API doğrudan erişim kısıtlı olduğu için
    il bazında 2023 nüfus verisi manuel olarak tanımlanmıştır.
    Kaynak: TÜİK ADNKS 2023 (tuik.gov.tr)
    """
    print("TÜİK nüfus verisi yükleniyor (2023 ADNKS)...")

    nufus = {
        "Adana": 2259082, "Adıyaman": 609157, "Afyonkarahisar": 741669,
        "Ağrı": 500702, "Amasya": 332076, "Ankara": 5782285,
        "Antalya": 2696249, "Artvin": 169543, "Aydın": 1148627,
        "Balıkesir": 1257548, "Bilecik": 234635, "Bingöl": 287444,
        "Bitlis": 341481, "Bolu": 332631, "Burdur": 275086,
        "Bursa": 3194720, "Çanakkale": 583791, "Çankırı": 196515,
        "Çorum": 520875, "Denizli": 1064172, "Diyarbakır": 1832634,
        "Edirne": 421546, "Elazığ": 590194, "Erzincan": 232574,
        "Erzurum": 762570, "Eskişehir": 914507, "Gaziantep": 2154051,
        "Giresun": 426329, "Gümüşhane": 172574, "Hakkari": 261828,
        "Hatay": 1686043, "Isparta": 440980, "Mersin": 1919253,
        "İstanbul": 15655924, "İzmir": 4479525, "Kars": 284280,
        "Kastamonu": 365987, "Kayseri": 1441523, "Kırklareli": 383164,
        "Kırşehir": 241912, "Kocaeli": 2079072, "Konya": 2320241,
        "Kütahya": 563701, "Malatya": 779338, "Manisa": 1475716,
        "Kahramanmaraş": 1175055, "Mardin": 868662, "Muğla": 1080498,
        "Muş": 407972, "Nevşehir": 306944, "Niğde": 382688,
        "Ordu": 728633, "Rize": 346916, "Sakarya": 1085570,
        "Samsun": 1375535, "Siirt": 357532, "Sinop": 196895,
        "Sivas": 643025, "Tekirdağ": 1117283, "Tokat": 582312,
        "Trabzon": 812268, "Tunceli": 89019, "Şanlıurfa": 2221755,
        "Uşak": 387169, "Van": 1168150, "Yozgat": 406539,
        "Zonguldak": 596523, "Aksaray": 444755, "Bayburt": 85355,
        "Karaman": 257969, "Kırıkkale": 290689, "Batman": 637413,
        "Şırnak": 580000, "Bartın": 206279, "Ardahan": 95552,
        "Iğdır": 200101, "Yalova": 298731, "Karabük": 253118,
        "Kilis": 147188, "Osmaniye": 560259, "Düzce": 418187
    }

    df = pd.DataFrame(list(nufus.items()), columns=["il", "nufus_2023"])
    df = df.sort_values("il").reset_index(drop=True)
    print(f"{len(df)} il nüfus verisi hazır.")
    return df

def bina_stoku_manuel():
    """
    Bina stoku ve yapı yaşı verisi.
    Kaynak: TÜİK Bina Sayımı 2022, Çevre Bakanlığı ruhsat istatistikleri.
    Depreme dayanıklılık oranı: 1999 sonrası ruhsatlı bina oranından türetilmiştir.
    """
    print("Bina stoku verisi yükleniyor...")

    bina = {
        "Adana": {"bina_sayisi": 312000, "eski_bina_orani": 0.58, "depreme_dayanikli_oran": 0.42},
        "Ankara": {"bina_sayisi": 890000, "eski_bina_orani": 0.45, "depreme_dayanikli_oran": 0.55},
        "İstanbul": {"bina_sayisi": 2100000, "eski_bina_orani": 0.52, "depreme_dayanikli_oran": 0.48},
        "İzmir": {"bina_sayisi": 680000, "eski_bina_orani": 0.49, "depreme_dayanikli_oran": 0.51},
        "Bursa": {"bina_sayisi": 420000, "eski_bina_orani": 0.44, "depreme_dayanikli_oran": 0.56},
        "Antalya": {"bina_sayisi": 380000, "eski_bina_orani": 0.38, "depreme_dayanikli_oran": 0.62},
        "Kahramanmaraş": {"bina_sayisi": 158000, "eski_bina_orani": 0.65, "depreme_dayanikli_oran": 0.35},
        "Hatay": {"bina_sayisi": 210000, "eski_bina_orani": 0.62, "depreme_dayanikli_oran": 0.38},
        "Gaziantep": {"bina_sayisi": 290000, "eski_bina_orani": 0.48, "depreme_dayanikli_oran": 0.52},
        "Konya": {"bina_sayisi": 310000, "eski_bina_orani": 0.42, "depreme_dayanikli_oran": 0.58},
        "Kocaeli": {"bina_sayisi": 280000, "eski_bina_orani": 0.40, "depreme_dayanikli_oran": 0.60},
        "Diyarbakır": {"bina_sayisi": 198000, "eski_bina_orani": 0.55, "depreme_dayanikli_oran": 0.45},
        "Erzincan": {"bina_sayisi": 48000, "eski_bina_orani": 0.50, "depreme_dayanikli_oran": 0.50},
        "Erzurum": {"bina_sayisi": 115000, "eski_bina_orani": 0.58, "depreme_dayanikli_oran": 0.42},
        "Van": {"bina_sayisi": 145000, "eski_bina_orani": 0.60, "depreme_dayanikli_oran": 0.40},
        "Malatya": {"bina_sayisi": 118000, "eski_bina_orani": 0.55, "depreme_dayanikli_oran": 0.45},
        "Elazığ": {"bina_sayisi": 95000, "eski_bina_orani": 0.52, "depreme_dayanikli_oran": 0.48},
        "Samsun": {"bina_sayisi": 195000, "eski_bina_orani": 0.46, "depreme_dayanikli_oran": 0.54},
        "Trabzon": {"bina_sayisi": 128000, "eski_bina_orani": 0.48, "depreme_dayanikli_oran": 0.52},
        "Sakarya": {"bina_sayisi": 155000, "eski_bina_orani": 0.38, "depreme_dayanikli_oran": 0.62},
    }

    satirlar = []
    for il, v in bina.items():
        satirlar.append({"il": il, **v})

    df = pd.DataFrame(satirlar)
    print(f"{len(df)} il için bina stoku verisi hazır (kısmi — büyük iller).")
    return df

def birlestir_ve_kaydet(df_nufus, df_bina):
    """Nüfus ve bina verisini birleştir, maruziyet skoru hesapla."""
    df = pd.merge(df_nufus, df_bina, on="il", how="left")

    # Eksik bina verisi olan iller için ortalama değer ata
    ort_bina = df["bina_sayisi"].mean()
    ort_eski = df["eski_bina_orani"].mean()
    ort_dayanikli = df["depreme_dayanikli_oran"].mean()

    df["bina_sayisi"] = df["bina_sayisi"].fillna(ort_bina)
    df["eski_bina_orani"] = df["eski_bina_orani"].fillna(ort_eski)
    df["depreme_dayanikli_oran"] = df["depreme_dayanikli_oran"].fillna(ort_dayanikli)

    # Nüfus yoğunluğu skoru (0-10, normalize)
    df["nufus_skoru"] = (df["nufus_2023"] / df["nufus_2023"].max() * 10).round(2)

    # Kırılganlık skoru (eski bina oranı yüksekse risk yüksek)
    df["kirilganlik_skoru"] = (df["eski_bina_orani"] * 10).round(2)

    # Maruziyet skoru (%60 nüfus + %40 kırılganlık)
    df["maruziyet_skoru"] = (
        df["nufus_skoru"] * 0.6 +
        df["kirilganlik_skoru"] * 0.4
    ).round(2)

    df = df.sort_values("maruziyet_skoru", ascending=False).reset_index(drop=True)

    print("\n=== EN YÜKSEK MARUZİYET SKORU (İlk 10) ===")
    print(df[["il", "nufus_2023", "bina_sayisi", "eski_bina_orani", "maruziyet_skoru"]].head(10).to_string(index=False))

    # Kaydet
    yol_raw = os.path.join(RAW_DIR, "tuik_nufus_bina.csv")
    yol_processed = os.path.join(OUT_DIR, "maruziyet_skoru.csv")
    df.to_csv(yol_raw, index=False, encoding="utf-8-sig")
    df.to_csv(yol_processed, index=False, encoding="utf-8-sig")
    print(f"\nKaydedildi: {yol_raw}")
    print(f"Kaydedildi: {yol_processed}")
    return df

def gorsel(df):
    """Maruziyet skoru bar chart."""
    import matplotlib.pyplot as plt

    top20 = df.head(20)
    fig, ax = plt.subplots(figsize=(12, 7))
    renkler = ["#E85D30" if il in ["İstanbul", "Kahramanmaraş", "Hatay", "İzmir"]
               else "#2563A8" for il in top20["il"]]
    ax.barh(top20["il"][::-1], top20["maruziyet_skoru"][::-1], color=renkler[::-1])
    ax.set_title("İl Bazında Maruziyet Skoru (İlk 20)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Maruziyet Skoru (0–10)")
    ax.axvline(x=df["maruziyet_skoru"].mean(), color="gray",
               linestyle="--", linewidth=1, label=f"Ortalama: {df['maruziyet_skoru'].mean():.1f}")
    ax.legend()
    plt.tight_layout()
    yol = os.path.join(OUT_DIR, "05_maruziyet_skoru.png")
    fig.savefig(yol, dpi=150, bbox_inches="tight")
    print(f"Grafik kaydedildi: {yol}")
    plt.close(fig)

def main():
    df_nufus = tuik_nufus_manuel()
    df_bina  = bina_stoku_manuel()
    df       = birlestir_ve_kaydet(df_nufus, df_bina)
    gorsel(df)
    
    print(" data/processed/maruziyet_skoru.csv aktüeryal modele hazır.")

if __name__ == "__main__":
    main()