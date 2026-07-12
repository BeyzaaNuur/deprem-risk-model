# ============================================================
#  DEPREM RİSK MODELİ — AKTÜERİYAL ANALİZ
#  Branch: feature/actuarial-model
#  Yazar: (senin adın)
# ============================================================

# ── 1. PAKET KURULUM VE YÜKLEME ─────────────────────────────
gerekli_paketler <- c("actuar", "fitdistrplus", "MASS", "ggplot2", "readr", "dplyr")

eksik <- gerekli_paketler[!gerekli_paketler %in% installed.packages()[, "Package"]]
if (length(eksik) > 0) {
  install.packages(eksik, dependencies = TRUE)
}

lapply(gerekli_paketler, library, character.only = TRUE)

cat("✓ Tüm paketler yüklendi.\n")

# ── 2. VERİ YÜKLEME ─────────────────────────────────────────
cat("Veriler yükleniyor...\n")

sismik      <- read_csv("data/processed/il_sismik_istatistik.csv")
maruziyet   <- read_csv("data/processed/maruziyet_skoru.csv")
sigorta     <- read_csv("data/processed/dask_sigortacilik.csv")
depremler   <- read_csv("data/raw/depremler_birlesik.csv")

cat("✓ Veriler yüklendi.\n")
cat("  - Sismik istatistik:", nrow(sismik), "il\n")
cat("  - Maruziyet skoru:  ", nrow(maruziyet), "il\n")
cat("  - DASK sigortacılık:", nrow(sigorta), "il\n")
cat("  - Deprem kaydı:     ", nrow(depremler), "adet\n")

# ── 3. HASAR DAĞILIM MODELİ ─────────────────────────────────
cat("\n[ADIM 3] Hasar dağılım modeli kuruluyor...\n")

# Büyüklük verisini çek — kolon adı "buyukluk" veya "magnitude" olabilir
mag_col <- intersect(c("buyukluk", "magnitude", "Buyukluk", "Magnitude"),
                     names(depremler))[1]
if (is.na(mag_col)) stop("Büyüklük kolonu bulunamadı. Kolon adlarını kontrol edin.")

buyukluk <- depremler[[mag_col]]
buyukluk <- buyukluk[!is.na(buyukluk) & buyukluk > 0]

cat("  Büyüklük verisi:", length(buyukluk), "kayıt (sıfır/NA temizlendi)\n")

# Dağılım uydurma
fit_lognormal <- fitdist(buyukluk, "lnorm", method = "mle")
fit_gamma     <- fitdist(buyukluk, "gamma", method = "mle")

# Pareto: actuar paketi — "pareto1" veya "pareto" kullanılır
# Pareto için büyüklük > xmin şartı gerekir; xmin olarak medyan alıyoruz
xmin <- median(buyukluk)
buyukluk_pareto <- buyukluk[buyukluk >= xmin]
fit_pareto <- tryCatch(
  fitdist(buyukluk_pareto, "pareto1", start = list(min = xmin, shape = 1.5),
          method = "mle"),
  error = function(e) {
    message("  Pareto1 hata verdi, pareto deneniyor: ", e$message)
    fitdist(buyukluk_pareto, "pareto", start = list(shape = 1.5, scale = xmin),
            method = "mle")
  }
)

# AIC karşılaştırması
aic_tablo <- data.frame(
  Dagilim = c("Lognormal", "Gamma", "Pareto"),
  AIC     = c(fit_lognormal$aic, fit_gamma$aic, fit_pareto$aic),
  BIC     = c(fit_lognormal$bic, fit_gamma$bic, fit_pareto$bic)
) |> arrange(AIC)

cat("\n  AIC Karşılaştırması:\n")
print(aic_tablo)

# KS testi
ks_lognormal <- ks.test(buyukluk, "plnorm",
                         fit_lognormal$estimate["meanlog"],
                         fit_lognormal$estimate["sdlog"])
ks_gamma     <- ks.test(buyukluk, "pgamma",
                         fit_gamma$estimate["shape"],
                         fit_gamma$estimate["rate"])

cat("\n  KS Testi p-değerleri:\n")
cat("    Lognormal:", round(ks_lognormal$p.value, 4), "\n")
cat("    Gamma:    ", round(ks_gamma$p.value, 4), "\n")

en_iyi_dagilim <- aic_tablo$Dagilim[1]
cat("\n  ✓ En iyi dağılım (en düşük AIC):", en_iyi_dagilim, "\n")

# Görselleştirme
png("data/processed/dagilim_uyum_grafigi.png", width = 900, height = 600)
denscomp(
  list(fit_lognormal, fit_gamma, fit_pareto),
  legendtext = c("Lognormal", "Gamma", "Pareto"),
  main = "Büyüklük Verisi — Dağılım Uyum Karşılaştırması"
)
dev.off()
cat("  ✓ Grafik kaydedildi: data/processed/dagilim_uyum_grafigi.png\n")

# ── 4. EAL HESABI ────────────────────────────────────────────
cat("\n[ADIM 4] Beklenen Yıllık Hasar (EAL) hesaplanıyor...\n")

# Sismik istatistik tablosunda beklenen hasar oranı veya yıllık aşılma olasılığı
# Kolon adları esnek tutuldu:
#   "ort_buyukluk" / "mean_magnitude", "yillik_frekans" / "annual_freq", "hasar_orani" / "loss_ratio"
sicaklik_kolon <- function(df, secenekler) {
  bulunan <- intersect(secenekler, names(df))
  if (length(bulunan) == 0) return(NULL)
  bulunan[1]
}

buyukluk_col  <- sicaklik_kolon(sismik, c("ort_buyukluk", "mean_magnitude", "buyukluk", "magnitude"))
frekans_col   <- sicaklik_kolon(sismik, c("yillik_frekans", "annual_freq", "frekans", "freq"))
hasar_col     <- sicaklik_kolon(sismik, c("hasar_orani", "loss_ratio", "hasar", "loss"))
il_col_sismik <- sicaklik_kolon(sismik, c("il", "il_adi", "province", "sehir"))

# EAL = ortalama büyüklük × yıllık frekans × hasar oranı (varsa)
# Yoksa: sismik skordan proxy EAL üret
if (!is.null(buyukluk_col) && !is.null(frekans_col)) {
  eal_ham <- sismik[[buyukluk_col]] * sismik[[frekans_col]]
  if (!is.null(hasar_col)) eal_ham <- eal_ham * sismik[[hasar_col]]
} else {
  # Fallback: mevcut sayısal kolonların ortalamasından skor üret
  sayisal_kolonlar <- sismik |> select(where(is.numeric))
  eal_ham <- rowMeans(sayisal_kolonlar, na.rm = TRUE)
  cat("  ⚠ EAL için proxy değer kullanıldı (kolon adları eşleşmedi).\n")
}

# 0–10 normalize
normalize_0_10 <- function(x) {
  mn <- min(x, na.rm = TRUE)
  mx <- max(x, na.rm = TRUE)
  if (mx == mn) return(rep(5, length(x)))
  (x - mn) / (mx - mn) * 10
}

sismik$EAL_normalize <- normalize_0_10(eal_ham)
cat("  ✓ EAL normalize edildi (0–10).\n")

# ── 5. BİLEŞİK RİSK SKORU ───────────────────────────────────
cat("\n[ADIM 5] Bileşik risk skoru hesaplanıyor...\n")

# Ağırlıklar
w_sismik     <- 0.40  # Sismik tehlike
w_maruziyet  <- 0.30  # Maruziyet
w_kirilganlik <- 0.20 # Kırılganlık
w_sigorta    <- 0.10  # Sigortalılık açığı

# IL sütununu bul (her tabloda ortak)
il_col <- function(df) {
  intersect(c("il", "il_adi", "province", "sehir", "IL", "IL_ADI"), names(df))[1]
}

# Tabloları birleştir
ana_tablo <- sismik |>
  rename(IL = !!il_col(sismik))

# Maruziyet skorunu birleştir
mar_skor_col <- intersect(c("maruziyet_skoru", "exposure_score", "skor", "score"),
                           names(maruziyet))[1]
if (!is.na(mar_skor_col)) {
  maruziyet <- maruziyet |> rename(IL = !!il_col(maruziyet))
  ana_tablo <- ana_tablo |>
    left_join(maruziyet |> select(IL, maruziyet_skor = !!mar_skor_col), by = "IL")
} else {
  ana_tablo$maruziyet_skor <- NA_real_
}

# DASK sigortacılık verisi — sigortalılık oranı
sig_col <- intersect(c("sigortalilık_orani", "insurance_rate", "dask_orani", "oran", "rate"),
                      names(sigorta))[1]
if (!is.na(sig_col)) {
  sigorta <- sigorta |> rename(IL = !!il_col(sigorta))
  ana_tablo <- ana_tablo |>
    left_join(sigorta |> select(IL, sigorta_oran = !!sig_col), by = "IL")
} else {
  ana_tablo$sigorta_oran <- NA_real_
}

# Kırılganlık proxy: sismik tabloda kırılganlık kolonu var mı?
kirilgan_col <- intersect(c("kirilganlik", "vulnerability", "kirilganlik_skoru", "vuln"),
                           names(ana_tablo))[1]
if (!is.na(kirilgan_col)) {
  ana_tablo$kirilganlik_norm <- normalize_0_10(ana_tablo[[kirilgan_col]])
} else {
  # EAL'ın tersini proxy olarak kullan (yüksek hasar = yüksek kırılganlık)
  ana_tablo$kirilganlik_norm <- ana_tablo$EAL_normalize
  cat("  ⚠ Kırılganlık için EAL proxy kullanıldı.\n")
}

# Sigortalılık açığı = (1 - sigortalılık_oranı) × 10
if (any(!is.na(ana_tablo$sigorta_oran))) {
  oran <- ana_tablo$sigorta_oran
  # Oran 0–1 arasındaysa doğrudan kullan, 0–100 arasındaysa 100'e böl
  if (max(oran, na.rm = TRUE) > 1) oran <- oran / 100
  ana_tablo$sigortasizlik_norm <- (1 - oran) * 10
} else {
  ana_tablo$sigortasizlik_norm <- 5  # veri yoksa orta değer
  cat("  ⚠ Sigortalılık açığı için varsayılan değer (5) kullanıldı.\n")
}

# Maruziyet normalizasyonu
if (any(!is.na(ana_tablo$maruziyet_skor))) {
  ana_tablo$maruziyet_norm <- normalize_0_10(ana_tablo$maruziyet_skor)
} else {
  ana_tablo$maruziyet_norm <- ana_tablo$EAL_normalize
  cat("  ⚠ Maruziyet için EAL proxy kullanıldı.\n")
}

# Bileşik skor
ana_tablo$bilesik_risk_skoru <-
  w_sismik      * ana_tablo$EAL_normalize       +
  w_maruziyet   * ana_tablo$maruziyet_norm       +
  w_kirilganlik * ana_tablo$kirilganlik_norm     +
  w_sigorta     * ana_tablo$sigortasizlik_norm

cat("  ✓ Bileşik risk skoru hesaplandı.\n")

# ── 6. MONTE CARLO SİMÜLASYONU ──────────────────────────────
cat("\n[ADIM 6] Monte Carlo simülasyonu (10.000 iterasyon) çalışıyor...\n")

set.seed(42)
n_iter <- 10000
n_il   <- nrow(ana_tablo)

# Her iterasyonda ağırlıklara küçük Gaussian gürültü ekle
# ve skoru yeniden hesapla → CI üret
mc_sonuclar <- matrix(NA_real_, nrow = n_iter, ncol = n_il)

for (i in seq_len(n_iter)) {
  # Ağırlıklara ±%10 rastgele gürültü
  w_s  <- pmax(0, w_sismik      + rnorm(1, 0, 0.04))
  w_m  <- pmax(0, w_maruziyet   + rnorm(1, 0, 0.03))
  w_k  <- pmax(0, w_kirilganlik + rnorm(1, 0, 0.02))
  w_g  <- pmax(0, w_sigorta     + rnorm(1, 0, 0.01))
  
  # Yeniden normalize et (toplam = 1)
  toplam <- w_s + w_m + w_k + w_g
  w_s <- w_s / toplam; w_m <- w_m / toplam
  w_k <- w_k / toplam; w_g <- w_g / toplam

  # Bileşen skorlarına da varyasyon ekle
  eal_v  <- pmin(10, pmax(0, ana_tablo$EAL_normalize      + rnorm(n_il, 0, 0.3)))
  mar_v  <- pmin(10, pmax(0, ana_tablo$maruziyet_norm      + rnorm(n_il, 0, 0.3)))
  kir_v  <- pmin(10, pmax(0, ana_tablo$kirilganlik_norm    + rnorm(n_il, 0, 0.2)))
  sig_v  <- pmin(10, pmax(0, ana_tablo$sigortasizlik_norm  + rnorm(n_il, 0, 0.1)))

  mc_sonuclar[i, ] <- w_s * eal_v + w_m * mar_v + w_k * kir_v + w_g * sig_v
}

# %95 güven aralıkları
ci_alt  <- apply(mc_sonuclar, 2, quantile, probs = 0.025)
ci_ust  <- apply(mc_sonuclar, 2, quantile, probs = 0.975)
mc_orta <- apply(mc_sonuclar, 2, mean)

ana_tablo$mc_ortalama <- mc_orta
ana_tablo$ci_alt_95   <- ci_alt
ana_tablo$ci_ust_95   <- ci_ust

cat("  ✓ Monte Carlo tamamlandı.\n")
cat("  ✓ %95 Güven Aralıkları hesaplandı.\n")

# ── 7. ÇIKTI: il_risk_skoru.csv ─────────────────────────────
cat("\n[ADIM 7] Sonuçlar kaydediliyor...\n")

il_risk_skoru <- ana_tablo |>
  select(
    il                = IL,
    sismik_tehlike    = EAL_normalize,
    maruziyet         = maruziyet_norm,
    kirilganlik       = kirilganlik_norm,
    sigortasizlik_acigi = sigortasizlik_norm,
    bilesik_risk_skoru,
    mc_ortalama,
    ci_alt_95,
    ci_ust_95
  ) |>
  arrange(desc(bilesik_risk_skoru))

write_csv(il_risk_skoru, "data/processed/il_risk_skoru.csv")
cat("  ✓ data/processed/il_risk_skoru.csv kaydedildi!\n")

# Özet tablo
cat("\n  En Riskli 10 İl:\n")
print(head(il_risk_skoru |> select(il, bilesik_risk_skoru, ci_alt_95, ci_ust_95), 10))

# ── 8. GÖRSEL: Risk Sıralaması ───────────────────────────────
p <- ggplot(head(il_risk_skoru, 20), aes(x = reorder(il, bilesik_risk_skoru),
                                           y = bilesik_risk_skoru)) +
  geom_col(fill = "#c0392b", alpha = 0.85) +
  geom_errorbar(aes(ymin = ci_alt_95, ymax = ci_ust_95), width = 0.3, color = "#2c3e50") +
  coord_flip() +
  labs(
    title    = "İl Bazlı Deprem Risk Skoru (En Riskli 20 İl)",
    subtitle = "Çubuklar: Bileşik skor | Hata çubukları: %95 MC Güven Aralığı",
    x = "İl", y = "Risk Skoru (0–10)"
  ) +
  theme_minimal(base_size = 13) +
  theme(plot.title = element_text(face = "bold"))

ggsave("data/processed/il_risk_siralamasi.png", p, width = 10, height = 8, dpi = 150)
cat("  ✓ Görsel kaydedildi: data/processed/il_risk_siralamasi.png\n")

cat("\n╔══════════════════════════════════════════╗\n")
cat("║  TÜM ADIMLAR TAMAMLANDI                 ║\n")
cat("║  → data/processed/il_risk_skoru.csv     ║\n")
cat("╚══════════════════════════════════════════╝\n")
