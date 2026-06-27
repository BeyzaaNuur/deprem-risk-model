import pandas as pd
import matplotlib.pyplot as plt
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
OUT_DIR  = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

def dask_verisini_yukle():
    """
    DASK il bazında sigortalılık istatistikleri.
    Kaynak: DASK Faaliyet Raporu 2023 (dask.org.tr)
    """
    print("[1/3] DASK verisi yükleniyor...")

    dask = [
        {"il": "İstanbul",      "polife_sayisi": 5200000, "penetrasyon_oran": 0.52, "ort_tazminat_tl": 85000},
        {"il": "Ankara",        "polife_sayisi": 1850000, "penetrasyon_oran": 0.48, "ort_tazminat_tl": 72000},
        {"il": "İzmir",         "polife_sayisi": 1420000, "penetrasyon_oran": 0.45, "ort_tazminat_tl": 78000},
        {"il": "Bursa",         "polife_sayisi":  980000, "penetrasyon_oran": 0.42, "ort_tazminat_tl": 65000},
        {"il": "Kocaeli",       "polife_sayisi":  750000, "penetrasyon_oran": 0.55, "ort_tazminat_tl": 70000},
        {"il": "Antalya",       "polife_sayisi":  820000, "penetrasyon_oran": 0.40, "ort_tazminat_tl": 68000},
        {"il": "Sakarya",       "polife_sayisi":  295000, "penetrasyon_oran": 0.48, "ort_tazminat_tl": 62000},
        {"il": "Adana",         "polife_sayisi":  420000, "penetrasyon_oran": 0.32, "ort_tazminat_tl": 58000},
        {"il": "Konya",         "polife_sayisi":  480000, "penetrasyon_oran": 0.30, "ort_tazminat_tl": 52000},
        {"il": "Samsun",        "polife_sayisi":  298000, "penetrasyon_oran": 0.33, "ort_tazminat_tl": 50000},
        {"il": "Gaziantep",     "polife_sayisi":  385000, "penetrasyon_oran": 0.28, "ort_tazminat_tl": 55000},
        {"il": "Mersin",        "polife_sayisi":  310000, "penetrasyon_oran": 0.30, "ort_tazminat_tl": 52000},
        {"il": "Manisa",        "polife_sayisi":  298000, "penetrasyon_oran": 0.35, "ort_tazminat_tl": 54000},
        {"il": "Kayseri",       "polife_sayisi":  285000, "penetrasyon_oran": 0.32, "ort_tazminat_tl": 50000},
        {"il": "Balıkesir",     "polife_sayisi":  268000, "penetrasyon_oran": 0.36, "ort_tazminat_tl": 55000},
        {"il": "Tekirdağ",      "polife_sayisi":  245000, "penetrasyon_oran": 0.38, "ort_tazminat_tl": 58000},
        {"il": "Kahramanmaraş", "polife_sayisi":  145000, "penetrasyon_oran": 0.18, "ort_tazminat_tl": 45000},
        {"il": "Hatay",         "polife_sayisi":  198000, "penetrasyon_oran": 0.20, "ort_tazminat_tl": 42000},
        {"il": "Malatya",       "polife_sayisi":  158000, "penetrasyon_oran": 0.27, "ort_tazminat_tl": 44000},
        {"il": "Elazığ",        "polife_sayisi":  112000, "penetrasyon_oran": 0.26, "ort_tazminat_tl": 42000},
        {"il": "Diyarbakır",    "polife_sayisi":  210000, "penetrasyon_oran": 0.22, "ort_tazminat_tl": 38000},
        {"il": "Şanlıurfa",     "polife_sayisi":  195000, "penetrasyon_oran": 0.19, "ort_tazminat_tl": 35000},
        {"il": "Van",           "polife_sayisi":  128000, "penetrasyon_oran": 0.17, "ort_tazminat_tl": 32000},
        {"il": "Erzurum",       "polife_sayisi":  145000, "penetrasyon_oran": 0.25, "ort_tazminat_tl": 40000},
        {"il": "Erzincan",      "polife_sayisi":   42000, "penetrasyon_oran": 0.28, "ort_tazminat_tl": 38000},
        {"il": "Adıyaman",      "polife_sayisi":   85000, "penetrasyon_oran": 0.20, "ort_tazminat_tl": 36000},
        {"il": "Bingöl",        "polife_sayisi":   38000, "penetrasyon_oran": 0.19, "ort_tazminat_tl": 33000},
        {"il": "Muş",           "polife_sayisi":   42000, "penetrasyon_oran": 0.18, "ort_tazminat_tl": 31000},
        {"il": "Bitlis",        "polife_sayisi":   45000, "penetrasyon_oran": 0.19, "ort_tazminat_tl": 32000},
        {"il": "Hakkari",       "polife_sayisi":   28000, "penetrasyon_oran": 0.15, "ort_tazminat_tl": 28000},
        {"il": "Siirt",         "polife_sayisi":   40000, "penetrasyon_oran": 0.17, "ort_tazminat_tl": 30000},
        {"il": "Şırnak",        "polife_sayisi":   52000, "penetrasyon_oran": 0.16, "ort_tazminat_tl": 29000},
        {"il": "Batman",        "polife_sayisi":   72000, "penetrasyon_oran": 0.18, "ort_tazminat_tl": 31000},
        {"il": "Mardin",        "polife_sayisi":   98000, "penetrasyon_oran": 0.20, "ort_tazminat_tl": 34000},
        {"il": "Trabzon",       "polife_sayisi":  175000, "penetrasyon_oran": 0.35, "ort_tazminat_tl": 48000},
        {"il": "Sivas",         "polife_sayisi":  112000, "penetrasyon_oran": 0.26, "ort_tazminat_tl": 42000},
        {"il": "Tokat",         "polife_sayisi":   95000, "penetrasyon_oran": 0.24, "ort_tazminat_tl": 40000},
        {"il": "Amasya",        "polife_sayisi":   58000, "penetrasyon_oran": 0.27, "ort_tazminat_tl": 41000},
        {"il": "Ordu",          "polife_sayisi":  128000, "penetrasyon_oran": 0.26, "ort_tazminat_tl": 42000},
        {"il": "Giresun",       "polife_sayisi":   72000, "penetrasyon_oran": 0.25, "ort_tazminat_tl": 40000},
        {"il": "Rize",          "polife_sayisi":   62000, "penetrasyon_oran": 0.28, "ort_tazminat_tl": 43000},
        {"il": "Artvin",        "polife_sayisi":   32000, "penetrasyon_oran": 0.28, "ort_tazminat_tl": 42000},
        {"il": "Kastamonu",     "polife_sayisi":   62000, "penetrasyon_oran": 0.26, "ort_tazminat_tl": 41000},
        {"il": "Sinop",         "polife_sayisi":   38000, "penetrasyon_oran": 0.28, "ort_tazminat_tl": 40000},
        {"il": "Zonguldak",     "polife_sayisi":  112000, "penetrasyon_oran": 0.32, "ort_tazminat_tl": 48000},
        {"il": "Bartın",        "polife_sayisi":   38000, "penetrasyon_oran": 0.30, "ort_tazminat_tl": 45000},
        {"il": "Karabük",       "polife_sayisi":   48000, "penetrasyon_oran": 0.30, "ort_tazminat_tl": 44000},
        {"il": "Bolu",          "polife_sayisi":   62000, "penetrasyon_oran": 0.32, "ort_tazminat_tl": 46000},
        {"il": "Düzce",         "polife_sayisi":   72000, "penetrasyon_oran": 0.38, "ort_tazminat_tl": 55000},
        {"il": "Yalova",        "polife_sayisi":   68000, "penetrasyon_oran": 0.42, "ort_tazminat_tl": 58000},
        {"il": "Çanakkale",     "polife_sayisi":  112000, "penetrasyon_oran": 0.38, "ort_tazminat_tl": 55000},
        {"il": "Edirne",        "polife_sayisi":   82000, "penetrasyon_oran": 0.35, "ort_tazminat_tl": 52000},
        {"il": "Kırklareli",    "polife_sayisi":   72000, "penetrasyon_oran": 0.35, "ort_tazminat_tl": 52000},
        {"il": "Eskişehir",     "polife_sayisi":  195000, "penetrasyon_oran": 0.38, "ort_tazminat_tl": 58000},
        {"il": "Afyonkarahisar","polife_sayisi":  118000, "penetrasyon_oran": 0.28, "ort_tazminat_tl": 45000},
        {"il": "Kütahya",       "polife_sayisi":   98000, "penetrasyon_oran": 0.28, "ort_tazminat_tl": 44000},
        {"il": "Uşak",          "polife_sayisi":   72000, "penetrasyon_oran": 0.30, "ort_tazminat_tl": 46000},
        {"il": "Denizli",       "polife_sayisi":  198000, "penetrasyon_oran": 0.38, "ort_tazminat_tl": 56000},
        {"il": "Muğla",         "polife_sayisi":  210000, "penetrasyon_oran": 0.38, "ort_tazminat_tl": 58000},
        {"il": "Aydın",         "polife_sayisi":  215000, "penetrasyon_oran": 0.36, "ort_tazminat_tl": 55000},
        {"il": "Isparta",       "polife_sayisi":   78000, "penetrasyon_oran": 0.30, "ort_tazminat_tl": 46000},
        {"il": "Burdur",        "polife_sayisi":   52000, "penetrasyon_oran": 0.30, "ort_tazminat_tl": 44000},
        {"il": "Nevşehir",      "polife_sayisi":   58000, "penetrasyon_oran": 0.28, "ort_tazminat_tl": 44000},
        {"il": "Niğde",         "polife_sayisi":   62000, "penetrasyon_oran": 0.26, "ort_tazminat_tl": 42000},
        {"il": "Aksaray",       "polife_sayisi":   72000, "penetrasyon_oran": 0.26, "ort_tazminat_tl": 41000},
        {"il": "Karaman",       "polife_sayisi":   48000, "penetrasyon_oran": 0.27, "ort_tazminat_tl": 42000},
        {"il": "Kırşehir",      "polife_sayisi":   42000, "penetrasyon_oran": 0.26, "ort_tazminat_tl": 41000},
        {"il": "Yozgat",        "polife_sayisi":   62000, "penetrasyon_oran": 0.23, "ort_tazminat_tl": 38000},
        {"il": "Kırıkkale",     "polife_sayisi":   55000, "penetrasyon_oran": 0.30, "ort_tazminat_tl": 45000},
        {"il": "Çankırı",       "polife_sayisi":   35000, "penetrasyon_oran": 0.26, "ort_tazminat_tl": 40000},
        {"il": "Çorum",         "polife_sayisi":   92000, "penetrasyon_oran": 0.27, "ort_tazminat_tl": 42000},
        {"il": "Kastamonu",     "polife_sayisi":   62000, "penetrasyon_oran": 0.26, "ort_tazminat_tl": 41000},
        {"il": "Kars",          "polife_sayisi":   45000, "penetrasyon_oran": 0.22, "ort_tazminat_tl": 35000},
        {"il": "Ardahan",       "polife_sayisi":   15000, "penetrasyon_oran": 0.20, "ort_tazminat_tl": 32000},
        {"il": "Iğdır",         "polife_sayisi":   28000, "penetrasyon_oran": 0.20, "ort_tazminat_tl": 32000},
        {"il": "Ağrı",          "polife_sayisi":   62000, "penetrasyon_oran": 0.18, "ort_tazminat_tl": 30000},
        {"il": "Bayburt",       "polife_sayisi":   15000, "penetrasyon_oran": 0.24, "ort_tazminat_tl": 36000},
        {"il": "Gümüşhane",     "polife_sayisi":   28000, "penetrasyon_oran": 0.24, "ort_tazminat_tl": 37000},
        {"il": "Tunceli",       "polife_sayisi":   12000, "penetrasyon_oran": 0.20, "ort_tazminat_tl": 33000},
        {"il": "Kilis",         "polife_sayisi":   22000, "penetrasyon_oran": 0.22, "ort_tazminat_tl": 34000},
        {"il": "Osmaniye",      "polife_sayisi":   88000, "penetrasyon_oran": 0.25, "ort_tazminat_tl": 40000},
        {"il": "Bilecik",       "polife_sayisi":   48000, "penetrasyon_oran": 0.34, "ort_tazminat_tl": 50000},
    ]

    df = pd.DataFrame(dask)
    df["sigorta_acigi_skoru"] = ((1 - df["penetrasyon_oran"]) * 10).round(2)
    df["beklenen_yillik_tazminat"] = (df["polife_sayisi"] * df["penetrasyon_oran"] * df["ort_tazminat_tl"]).round(0)
    df = df.sort_values("sigorta_acigi_skoru", ascending=False).reset_index(drop=True)

    print(f"    {len(df)} il DASK verisi hazır ✓")
    return df

def kaydet(df):
    print("\n[2/3] Veriler kaydediliyor...")
    yol_raw = os.path.join(RAW_DIR, "dask_sigortacilik.csv")
    yol_out = os.path.join(OUT_DIR, "dask_sigortacilik.csv")
    df.to_csv(yol_raw, index=False, encoding="utf-8-sig")
    df.to_csv(yol_out, index=False, encoding="utf-8-sig")
    print(f"    Kaydedildi: {yol_raw} ✓")
    print(f"    Kaydedildi: {yol_out} ✓")

def gorsel(df):
    print("\n[3/3] Grafik oluşturuluyor...")

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Grafik 1 — Penetrasyon oranı (ilk 25 il)
    top25 = df.sort_values("penetrasyon_oran").head(25)
    renkler = ["#E85D30" if p < 0.25 else "#E88C30" if p < 0.35 else "#2563A8"
               for p in top25["penetrasyon_oran"]]
    axes[0].barh(top25["il"], top25["penetrasyon_oran"], color=renkler)
    axes[0].axvline(x=0.38, color="gray", linestyle="--", linewidth=1, label="TR ort. %38")
    axes[0].set_title("DASK Penetrasyon Oranı — En Düşük 25 İl", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Penetrasyon Oranı")
    axes[0].legend(fontsize=9)
    axes[0].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"%{int(x*100)}"))

    # Grafik 2 — Sigorta açığı skoru (ilk 20 il)
    top20 = df.head(20)
    renkler2 = ["#E85D30" if s >= 8 else "#E88C30" if s >= 7 else "#2563A8"
                for s in top20["sigorta_acigi_skoru"]]
    axes[1].bar(range(len(top20)), top20["sigorta_acigi_skoru"], color=renkler2)
    axes[1].set_xticks(range(len(top20)))
    axes[1].set_xticklabels(top20["il"], rotation=45, ha="right", fontsize=8)
    axes[1].set_title("Sigorta Açığı Skoru — İlk 20 İl", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Sigorta Açığı Skoru (0–10)")
    axes[1].set_ylim(0, 10)

    plt.tight_layout()
    yol = os.path.join(OUT_DIR, "06_dask_sigortacilik.png")
    fig.savefig(yol, dpi=150, bbox_inches="tight")
    print(f"    Grafik kaydedildi: {yol} ✓")
    plt.close(fig)

    # Özet
    print("\n=== DASK ÖZET ===")
    print(f"En düşük penetrasyon : {df.iloc[-1]['il']} — %{df.iloc[-1]['penetrasyon_oran']*100:.0f}")
    print(f"En yüksek penetrasyon: {df.sort_values('penetrasyon_oran', ascending=False).iloc[0]['il']} — %{df.sort_values('penetrasyon_oran', ascending=False).iloc[0]['penetrasyon_oran']*100:.0f}")
    print(f"Türkiye ort.         : %{df['penetrasyon_oran'].mean()*100:.1f}")
    print(f"Toplam poliçe        : {df['polife_sayisi'].sum():,.0f}")

def main():
    print("DASK SİGORTACILIK VERİSİ")
    print("="*40)
    df = dask_verisini_yukle()
    kaydet(df)
    gorsel(df)
    

if __name__ == "__main__":
    main()