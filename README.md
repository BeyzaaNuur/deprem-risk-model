# Türkiye Deprem Risk Modeli


## Ekip
- Proje Yürütücüsü: [Beyza Nur DİNÇER] — KTÜ YBS (Python, Power BI)
- Proje Ortağı: [Elif ÇAKIR] — Marmara Aktüerya (R, modelleme)

## Proje Yapısı
- `data/raw/`        → Ham veriler (AFAD, TÜİK, DASK)
- `data/processed/`  → Temizlenmiş veriler
- `src/pipeline/`    → Python veri çekme & temizleme scriptleri
- `src/analysis/`    → R aktüeryal modelleme scriptleri
- `powerbi/`         → Power BI dosyaları
- `notebooks/`       → Keşifsel analiz (Jupyter)
- `docs/`            → Fizibilite raporu, referanslar

## Kurulum
pip install -r requirements.txt
