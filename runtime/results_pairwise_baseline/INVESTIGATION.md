# Panduan investigasi hasil pairwise

Hasil dipisahkan menurut `pair_type`, dengan nilai dan urutan baris yang sama seperti CSV gabungan. Skor tidak dihitung ulang. CSV, dokumentasi metodologi, dan laporan validasi asli tetap utuh.

| Kelompok | Pasangan | Panduan |
|---|---:|---|
| Within-flow | 411 | [Buka hasil dan contoh](within_flow/README.md) |
| Cross-flow | 298 | [Buka hasil dan contoh](cross_flow/README.md) |
| Total | 709 | [Jumlah per aplikasi](investigation_pair_counts.csv) |

Mulai dari satu aplikasi di salah satu folder. Baca ringkasan deskriptif, pilih pasangan dari `investigation_examples.csv`, lalu buka screenshot A/B melalui tautan di panduan folder. Contoh ekstrem dipilih per deskriptor, bukan berdasarkan skor gabungan.

Untuk membandingkan within-flow dan cross-flow, gunakan aplikasi dan deskriptor yang sama. Perhatikan jumlah pasangan, median, kuartil, dan rentang. Jangan menyimpulkan konsistensi atau signifikansi dari perbedaan rata-rata saja: pasangan berbagi screenshot dan tidak independen.

Validasi pemisahan memeriksa jenis flow, kesamaan ID antara distance/similarity, jumlah pasangan pada ringkasan, tidak adanya pasangan ganda antarkelompok, gabungan tepat 709 pasangan, serta SHA-256 CSV sumber yang tidak berubah. Ringkasan `all` tetap tersedia hanya pada hasil gabungan agar tidak terhitung dua kali.

[Metodologi lengkap](../PAIRWISE_METHODS.md) · [Laporan validasi awal](validation_report.md)

Tidak ada review visual baru, klasifikasi konsistensi, skor komposit, atau perhitungan graph pada pemisahan ini.
