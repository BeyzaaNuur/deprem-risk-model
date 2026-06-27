import geopandas as gpd
import pandas as pd
import requests
import zipfile
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
EXT_DIR  = os.path.join(BASE_DIR, "data", "external")
OUT_DIR  = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(EXT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# 1. Türkiye Shapefile İndir
# ─────────────────────────────────────────────
def shapefile_indir():
    shp_yol = os.path.join(EXT_DIR, "turkey_iller.shp")
    if os.path.exists(shp_yol):
        print("[1/5] Shapefile zaten mevcut, atlanıyor ✓")
        return shp_yol

    print("[1/5] Türkiye il sınır shapefile indiriliyor...")
    url = "https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_TUR_shp.zip"
    zip_yol = os.path.join(EXT_DIR, "turkey_gadm.zip")

    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(zip_yol, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print("    İndirildi, açılıyor...")

    with zipfile.ZipFile(zip_yol, "r") as z:
        z.extractall(EXT_DIR)

    # GADM level 1 = il sınırları
    gadm_shp = os.path.join(EXT_DIR, "gadm41_TUR_1.shp")
    if os.path.exists(gadm_shp):
        print(f"    Shapefile hazır: {gadm_shp} ✓")
        return gadm_shp
    else:
        print("    Hata: shapefile bulunamadı")
        return None

# ─────────────────────────────────────────────
# 2. Shapefile Yükle & Düzenle
# ─────────────────────────────────────────────
def shapefile_yukle(shp_yol):
    print("[2/5] Shapefile yükleniyor...")
    gdf = gpd.read_file(shp_yol)
    print(f"    {len(gdf)} il sınırı yüklendi ✓")
    print(f"    Sütunlar: {list(gdf.columns)}")

    # İl adını normalize et
    gdf = gdf.rename(columns={"NAME_1": "il"})
    gdf["il"] = gdf["il"].str.strip()

    # CRS kontrol
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    else:
        gdf = gdf.to_crs("EPSG:4326")

    return gdf[["il", "geometry"]]

# ─────────────────────────────────────────────
# 3. Deprem Verisi + Spatial Join
# ─────────────────────────────────────────────
def spatial_join(gdf_iller):
    print("[3/5] Deprem verisi yükleniyor & spatial join yapılıyor...")

    # Deprem verisini yükle
    dep_yol = os.path.join(RAW_DIR, "depremler_birlesik.csv")
    if not os.path.exists(dep_yol):
        dep_yol = os.path.join("data", "raw", "depremler_birlesik.csv")
    df_dep = pd.read_csv(dep_yol)
    df_dep = df_dep.dropna(subset=["enlem", "boylam"])
    print(f"    {len(df_dep)} deprem kaydı yüklendi")

    # GeoDataFrame'e çevir
    gdf_dep = gpd.GeoDataFrame(
        df_dep,
        geometry=gpd.points_from_xy(df_dep["boylam"], df_dep["enlem"]),
        crs="EPSG:4326"
    )

    # Spatial join — her deprem noktasına il ata
    joined = gpd.sjoin(gdf_dep, gdf_iller, how="left", predicate="within")
    joined = joined.rename(columns={"il": "il_adi"})

    # Eşleşemeyen noktalar (sınır dışı) için en yakın ili bul
    eslesmeyenler = joined[joined["il_adi"].isna()].copy()
    if not eslesmeyenler.empty:
        print(f"    {len(eslesmeyenler)} nokta sınır dışı — en yakın ile atanıyor...")
        joined_nearest = gpd.sjoin_nearest(
            eslesmeyenler[["buyukluk", "derinlik_km", "enlem", "boylam", "tarih", "kaynak", "yer", "geometry"]],
            gdf_iller,
            how="left"
        )
        joined_nearest = joined_nearest.rename(columns={"il": "il_adi"})
        joined.loc[joined["il_adi"].isna(), "il_adi"] = joined_nearest["il_adi"].values

    print(f"    Spatial join tamamlandı ✓")
    print(f"    Eşleşen il sayısı: {joined['il_adi'].nunique()}")
    return joined

# ─────────────────────────────────────────────
# 4. İl Bazında Sismik İstatistik
# ─────────────────────────────────────────────
def il_bazinda_istatistik(df_joined):
    print("[4/5] İl bazında sismik istatistik hesaplanıyor...")

    istatistik = df_joined.groupby("il_adi").agg(
        deprem_sayisi    = ("buyukluk", "count"),
        ort_buyukluk     = ("buyukluk", "mean"),
        max_buyukluk     = ("buyukluk", "max"),
        ort_derinlik     = ("derinlik_km", "mean"),
        m5_ustu          = ("buyukluk", lambda x: (x >= 5.0).sum()),
        m6_ustu          = ("buyukluk", lambda x: (x >= 6.0).sum()),
    ).reset_index()

    # Sismik tehlike skoru (0-10, normalize)
    istatistik["sismik_skor"] = (
        istatistik["deprem_sayisi"] / istatistik["deprem_sayisi"].max() * 5 +
        istatistik["max_buyukluk"]  / istatistik["max_buyukluk"].max()  * 3 +
        istatistik["m5_ustu"]       / istatistik["m5_ustu"].max()       * 2
    ).round(2)

    istatistik = istatistik.sort_values("sismik_skor", ascending=False).reset_index(drop=True)

    print("\n    === EN RİSKLİ 10 İL (Sismik Skor) ===")
    print(istatistik[["il_adi", "deprem_sayisi", "max_buyukluk", "m6_ustu", "sismik_skor"]].head(10).to_string(index=False))

    yol = os.path.join(OUT_DIR, "il_sismik_istatistik.csv")
    istatistik.to_csv(yol, index=False, encoding="utf-8-sig")
    print(f"\n    Kaydedildi: {yol} ✓")
    return istatistik

# ─────────────────────────────────────────────
# 5. Harita Görselleştirme
# ─────────────────────────────────────────────
def harita_gorsellestir(gdf_iller, istatistik):
    print("[5/5] Türkiye risk haritası oluşturuluyor...")

    gdf_merge = gdf_iller.merge(istatistik, left_on="il", right_on="il_adi", how="left")
    gdf_merge["sismik_skor"] = gdf_merge["sismik_skor"].fillna(0)

    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    gdf_merge.plot(
        column="sismik_skor",
        cmap="YlOrRd",
        linewidth=0.4,
        edgecolor="white",
        legend=True,
        legend_kwds={"label": "Sismik Tehlike Skoru (0–10)", "shrink": 0.6},
        ax=ax
    )

    # En riskli 5 ili etiketle
    top5 = istatistik.head(5)
    gdf_top5 = gdf_merge[gdf_merge["il_adi"].isin(top5["il_adi"])]
    for _, row in gdf_top5.iterrows():
        centroid = row.geometry.centroid
        ax.annotate(
            f"{row['il']}\n{row['sismik_skor']:.1f}",
            xy=(centroid.x, centroid.y),
            fontsize=7, ha="center", color="black",
            fontweight="bold"
        )

    ax.set_title("Türkiye İl Bazında Sismik Tehlike Skoru (1990–2024)", fontsize=14, fontweight="bold")
    ax.set_axis_off()
    plt.tight_layout()

    yol = os.path.join(OUT_DIR, "07_turkiye_risk_haritasi.png")
    fig.savefig(yol, dpi=150, bbox_inches="tight")
    print(f"    Harita kaydedildi: {yol} ✓")
    plt.close(fig)

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("SPATIAL JOIN — DEPREM × İL SINIRI EŞLEŞTİRME")
    print("="*50)

    shp_yol    = shapefile_indir()
    gdf_iller  = shapefile_yukle(shp_yol)
    df_joined  = spatial_join(gdf_iller)
    istatistik = il_bazinda_istatistik(df_joined)
    harita_gorsellestir(gdf_iller, istatistik)

    print("\n" + "="*50)
    print("SPATIAL JOIN TAMAMLANDI")
    print("Çıktılar:")
    print("  data/processed/il_sismik_istatistik.csv ")
    print("  data/processed/07_turkiye_risk_haritasi.png")
    print("="*50)

if __name__ == "__main__":
    main()