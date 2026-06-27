import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

# Dosya yolları
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
OUT_DIR  = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(OUT_DIR, exist_ok=True)

def yukle():
    yol = os.path.join(RAW_DIR, "depremler_birlesik.csv")
    df = pd.read_csv(yol, parse_dates=["tarih"])
    print(f"Veri yüklendi: {len(df)} kayıt")
    return df

def genel_bakis(df):
    print("\n=== GENEL BAKIŞ ===")
    print(df.describe().round(2))

def buyukluk_dagilimi(df):
    """Büyüklük histogramı."""
    fig, ax = plt.subplots(figsize=(10, 5))
    bins = [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0]
    ax.hist(df["buyukluk"], bins=bins, color="#2563A8", edgecolor="white", linewidth=0.5)
    ax.set_title("Deprem Büyüklük Dağılımı (M≥4.0, 1990–2024)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Büyüklük (Mw)")
    ax.set_ylabel("Deprem Sayısı")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    kaydet_grafik(fig, "01_buyukluk_dagilimi.png")

def yillik_frekans(df):
    """Yıllık deprem sayısı — 1999 ve 2023 vurgulu."""
    df["yil"] = df["tarih"].dt.year
    yillik = df.groupby("yil").size().reset_index(name="sayi")

    fig, ax = plt.subplots(figsize=(14, 5))
    renkler = ["#E85D30" if y in [1999, 2023] else "#2563A8" for y in yillik["yil"]]
    ax.bar(yillik["yil"], yillik["sayi"], color=renkler, width=0.7)

    # Etiketler
    for _, row in yillik[yillik["yil"].isin([1999, 2023])].iterrows():
        ax.annotate(
            f"{row['yil']}\n({row['sayi']} dep.)",
            xy=(row["yil"], row["sayi"]),
            xytext=(0, 8), textcoords="offset points",
            ha="center", fontsize=9, color="#E85D30", fontweight="bold"
        )

    ax.set_title("Yıllık Deprem Frekansı (M≥4.0, 1990–2024)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Yıl")
    ax.set_ylabel("Deprem Sayısı")
    ax.set_xticks(yillik["yil"])
    ax.set_xticklabels(yillik["yil"], rotation=45, ha="right", fontsize=8)
    plt.tight_layout()
    kaydet_grafik(fig, "02_yillik_frekans.png")

def derinlik_analizi(df):
    """Derinlik dağılımı — sığ vs derin."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df["derinlik_km"], bins=40, color="#5DC8A0", edgecolor="white", linewidth=0.5)
    ax.axvline(x=70, color="#E85D30", linestyle="--", linewidth=1.5, label="70 km (sığ sınırı)")
    ax.set_title("Deprem Derinlik Dağılımı", fontsize=13, fontweight="bold")
    ax.set_xlabel("Derinlik (km)")
    ax.set_ylabel("Deprem Sayısı")
    ax.legend()

    sig = len(df[df["derinlik_km"] <= 70])
    derin = len(df[df["derinlik_km"] > 70])
    ax.text(0.98, 0.95, f"Sığ (≤70 km): {sig:,}\nDerin (>70 km): {derin:,}",
            transform=ax.transAxes, ha="right", va="top", fontsize=9,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

    plt.tight_layout()
    kaydet_grafik(fig, "03_derinlik_dagilimi.png")

def buyuk_depremler(df):
    """M6.0+ depremleri listele ve haritala."""
    buyuk = df[df["buyukluk"] >= 6.0].sort_values("buyukluk", ascending=False).reset_index(drop=True)
    print(f"\n=== M6.0+ DEPREMLER ({len(buyuk)} adet) ===")
    print(buyuk[["tarih", "buyukluk", "derinlik_km", "enlem", "boylam", "yer"]].head(20).to_string(index=False))

    # CSV olarak kaydet
    yol = os.path.join(OUT_DIR, "buyuk_depremler_m6plus.csv")
    buyuk.to_csv(yol, index=False, encoding="utf-8-sig")
    print(f"\nKaydedildi: {yol}")

    # Harita scatter
    fig, ax = plt.subplots(figsize=(12, 6))
    scatter = ax.scatter(
        buyuk["boylam"], buyuk["enlem"],
        c=buyuk["buyukluk"], cmap="YlOrRd",
        s=buyuk["buyukluk"] ** 3, alpha=0.7, edgecolors="gray", linewidth=0.3
    )
    plt.colorbar(scatter, ax=ax, label="Büyüklük (Mw)")
    ax.set_xlim(25, 45)
    ax.set_ylim(35, 43)
    ax.set_title("M6.0+ Deprem Dağılım Haritası (1990–2024)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Boylam")
    ax.set_ylabel("Enlem")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    kaydet_grafik(fig, "04_m6plus_harita.png")

def kaydet_grafik(fig, dosya_adi):
    yol = os.path.join(OUT_DIR, dosya_adi)
    fig.savefig(yol, dpi=150, bbox_inches="tight")
    print(f"Grafik kaydedildi: {yol}")
    plt.close(fig)

def main():
    df = yukle()
    genel_bakis(df)
    buyukluk_dagilimi(df)
    yillik_frekans(df)
    derinlik_analizi(df)
    buyuk_depremler(df)
    print("\nEDA tamamlandı. Grafikler data/processed/ klasöründe.")

if __name__ == "__main__":
    main()
    