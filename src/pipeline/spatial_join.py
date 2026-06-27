import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

def coografi_birlestirme():
    print("Coğrafi eşleştirme süreci başlıyor...")
    
    
    deprem_yolu = os.path.join("data", "raw", "depremler_birlesik.csv")
    if not os.path.exists(deprem_yolu):
        print("Hata: depremler_birlesik.csv bulunamadı! Önce afad_fetch.py çalıştırılmalı.")
        return
    
    df = pd.read_csv(deprem_yolu)
    print(f"Okunan deprem kaydı sayısı: {len(df)}")
    
    # Enlem ve boylam verilerinden coğrafi noktalar (Geometry) oluştur
    geometry = [Point(xy) for xy in zip(df['boylam'], df['enlem'])]
    # Deprem verisini coğrafi veri formatına (GeoDataFrame) çevir
    # WGS84 koordinat sistemi (EPSG:4326) kullanıyoruz
    gdf_deprem = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    
    # 2. Adım: Türkiye İlçe Sınırları Harita Dosyasını Yükle
    # NOT: Bu dosya henüz klasörünüzde yoksa hata verecektir, alta indirme notunu bıraktım.
    harita_yolu = os.path.join("data", "raw", "turkiye_ilceler.geojson")
    
    if not os.path.exists(harita_yolyu := harita_yolu):
        print(f"Hata: {harita_yolu} dosyası bulunamadı! Lütfen harita verisini ekleyin.")
        return
        
    gdf_harita = gpd.read_file(harita_yolu)
    
    # Harita koordinat sisteminin depremle aynı olduğundan emin ol
    if gdf_harita.crs != gdf_deprem.crs:
        gdf_harita = gdf_harita.to_crs(gdf_deprem.crs)
        
    print("Harita dosyası başarıyla yüklendi. Eşleştirme yapılıyor...")
    
    # 3. Adım: Spatial Join (Hangi nokta hangi ilçenin içinde?)
    # 'op=within' veya 'predicate=within' deprem noktası ilçenin İÇİNDEYSE eşleştirir
    bilesik_gdf = gpd.sjoin(gdf_deprem, gdf_harita, how="left", predicate="within")
    
    # 4. Adım: Sonucu yeni bir CSV olarak kaydet
    cikis_yolu = os.path.join("data", "processed", "depremler_ilce_eslesmis.csv")
    
    # Coğrafi geometry sütununu normal CSV'ye yazamayacağımız için düşürüp kaydediyoruz
    df_sonuc = pd.DataFrame(bilesik_gdf.drop(columns='geometry'))
    df_sonuc.to_csv(cikis_yolu, index=False, encoding="utf-8-sig")
    
    print(f"İşlem tamamlandı! İlçe eşleşmeli yeni veri şuraya kaydedildi: {cikis_yolu}")

if __name__ == "__main__":
    coografi_birlestirme()