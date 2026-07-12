import geopandas as gpd
import topojson as tp
import json
import os

# Klasör yolları
BASE_DIR = os.path.abspath(os.path.join(os.getcwd()))
EXT_DIR  = os.path.join(BASE_DIR, "data", "external")
OUT_DIR  = os.path.join(BASE_DIR, "powerbi")
os.makedirs(OUT_DIR, exist_ok=True)

IL_DUZELTME = {
    "K. Maras": "Kahramanmaraş", "Kahramanmaras": "Kahramanmaraş",
    "Sanliurfa": "Şanlıurfa", "Diyarbakir": "Diyarbakır",
    "Adiyaman": "Adıyaman", "Afyon": "Afyonkarahisar",
    "Balikesir": "Balıkesir", "Canakkale": "Çanakkale",
    "Cankiri": "Çankırı", "Corum": "Çorum",
    "Eskisehir": "Eskişehir", "Gumushane": "Gümüşhane",
    "Igdir": "Iğdır", "Istanbul": "İstanbul",
    "Izmir": "İzmir", "Kirikkale": "Kırıkkale",
    "Kirklareli": "Kırklareli", "Kirsehir": "Kırşehir",
    "Mugla": "Muğla", "Mus": "Muş",
    "Nigde": "Niğde", "Sirnak": "Şırnak",
    "Tekirdag": "Tekirdağ", "Usak": "Uşak",
    "Agri": "Ağrı", "Aydin": "Aydın",
    "Bingol": "Bingöl", "Elazig": "Elazığ",
    "Golcuk": "Kocaeli"
}

print("[1/3] Bilgisayardaki mevcut shapefile yükleniyor...")
shp_yol = os.path.join(EXT_DIR, "gadm41_TUR_1.shp")

if not os.path.exists(shp_yol):
    print(f"Hata: {shp_yol} bulunamadı! Lütfen data/external klasörünü kontrol et.")
else:
    gdf = gpd.read_file(shp_yol)
    
    # Amerika hatasını önlemek için sadece Türkiye katmanını filtrele
    if "GID_0" in gdf.columns:
        gdf = gdf[gdf["GID_0"] == "TUR"]
        
    gdf = gdf.rename(columns={"NAME_1": "il"})
    gdf["il"] = gdf["il"].str.strip().replace(IL_DUZELTME)
    gdf = gdf.to_crs("EPSG:4326")
    gdf = gdf[["il", "geometry"]]

    print("[2/3] Geometri basitleştiriliyor ve TopoJSON'a dönüştürülüyor...")
    gdf["geometry"] = gdf["geometry"].simplify(tolerance=0.01, preserve_topology=True)
    topo = tp.Topology(gdf, prequantize=False)
    topo_dict = json.loads(topo.to_json())

    print("[3/3] Sadece Türkiye'yi içeren dosya kaydediliyor...")
    yol = os.path.join(OUT_DIR, "turkiye_garanti.json")
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(topo_dict, f, ensure_ascii=False)
        
    print(f"\n✓ BAŞARILI! Yeni harita dosyan hazır: {yol}")