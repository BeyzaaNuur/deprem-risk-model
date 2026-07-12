import geopandas as gpd
import topojson as tp
import json
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
EXT_DIR  = os.path.join(BASE_DIR, "data", "external")
OUT_DIR  = os.path.join(BASE_DIR, "powerbi")
os.makedirs(OUT_DIR, exist_ok=True)


IL_DUZELTME = {
    "K. Maras": "Kahramanmaraş",
    "Kahramanmaras": "Kahramanmaraş",
    "Sanliurfa": "Şanlıurfa",
    "Diyarbakir": "Diyarbakır",
    "Adiyaman": "Adıyaman",
    "Afyon": "Afyonkarahisar",
    "Balikesir": "Balıkesir",
    "Canakkale": "Çanakkale",
    "Cankiri": "Çankırı",
    "Corum": "Çorum",
    "Eskisehir": "Eskişehir",
    "Gumushane": "Gümüşhane",
    "Igdir": "Iğdır",
    "Istanbul": "İstanbul",
    "Izmir": "İzmir",
    "Kirikkale": "Kırıkkale",
    "Kirklareli": "Kırklareli",
    "Kirsehir": "Kırşehir",
    "Mugla": "Muğla",
    "Mus": "Muş",
    "Nigde": "Niğde",
    "Sirnak": "Şırnak",
    "Tekirdag": "Tekirdağ",
    "Usak": "Uşak",
    "Agri": "Ağrı",
    "Aydin": "Aydın",
    "Bingol": "Bingöl",
    "Elazig": "Elazığ",
    "Golcuk": "Kocaeli",
}

def shapefile_yukle():
    print("[1/4] Shapefile yükleniyor...")
    shp_yol = os.path.join(EXT_DIR, "gadm41_TUR_1.shp")
    if not os.path.exists(shp_yol):
        raise FileNotFoundError(f"Hata: {shp_yol} bulunamadı! Lütfen Türkiye Shapefile dosyalarını ekleyin.")
        
    gdf = gpd.read_file(shp_yol)
    
    if "GID_0" in gdf.columns:
        gdf = gdf[gdf["GID_0"] == "TUR"]
    
    print(f"    {len(gdf)} Türkiye il sınırı başarıyla yüklendi ✓")

   
    gdf = gdf.rename(columns={"NAME_1": "il"})
    gdf["il"] = gdf["il"].str.strip()
    gdf["il"] = gdf["il"].replace(IL_DUZELTME)

    gdf = gdf.to_crs("EPSG:4326")

    gdf = gdf[["il", "geometry"]]
    return gdf

def geometriyi_basitlestir(gdf):
    """Power BI performansı için geometriyi basitleştirir (dosya boyutunu küçültür)."""
    print("[2/4] Geometri basitleştiriliyor (performans için)...")
    gdf["geometry"] = gdf["geometry"].simplify(tolerance=0.01, preserve_topology=True)
    print("    Basitleştirme tamamlandı ✓")
    return gdf

def topojson_olustur(gdf):
    print("[3/4] TopoJSON formatına dönüştürülüyor...")
    topo = tp.Topology(gdf, prequantize=False)
    topo_dict = json.loads(topo.to_json())
    print(f"    {len(gdf)} il TopoJSON'a dönüştürüldü ✓")
    return topo_dict

def kaydet(topo_dict):
    print("[4/4] Dosya kaydediliyor...")
    yol = os.path.join(OUT_DIR, "turkiye_iller.json")
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(topo_dict, f, ensure_ascii=False)

    boyut_kb = os.path.getsize(yol) / 1024
    print(f"    Kaydedildi: {yol} ✓")
    print(f"    Dosya boyutu: {boyut_kb:.1f} KB")
    return yol

def il_listesi_kontrol(gdf):
    """CSV'lerdeki il isimleriyle uyumu kontrol eder."""
    print("\n=== İL İSİM KONTROLÜ ===")
    print(f"Toplam il: {len(gdf)}")
    print("İlk 10 il:", sorted(gdf["il"].tolist())[:10])

    import pandas as pd
    risk_yol = os.path.join(BASE_DIR, "data", "processed", "il_risk_skoru_duzeltilmis.csv")
    if os.path.exists(risk_yol):
        df_risk = pd.read_csv(risk_yol)
        shape_iller = set(gdf["il"])
        risk_iller = set(df_risk["il"])

        eslesmeyen = risk_iller - shape_iller
        if eslesmeyen:
            print(f"\nUyarı: Risk skoru dosyasında olup shape'te OLMAYAN iller ({len(eslesmeyen)}):")
            print(f"  {sorted(eslesmeyen)}")
        else:
            print("\nTüm risk skoru illeri shape dosyasıyla eşleşiyor ✓")

def main():
    print("SHAPEFILE → TOPOJSON DÖNÜŞTÜRME (Power BI Shape Map için)")
    print("="*60)

   
    gdf = shapefile_yukle() 
    gdf = geometriyi_basitlestir(gdf)
    il_listesi_kontrol(gdf)
    topo_dict = topojson_olustur(gdf)
    yol = kaydet(topo_dict)

    print("\n" + "="*60)
    print("TAMAMLANDI")
    print(f"Power BI'da Shape Map görselinde kullanılacak dosya:")
    print(f"  {yol}")
    print("\nShape Map ayarlarında:")
    print("  Format → Shape → 'Add map' → bu dosyayı yükle")
    print("="*60)