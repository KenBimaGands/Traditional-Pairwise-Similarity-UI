# Investigasi hasil cross_flow

Terdapat **298 pasangan** dari lima aplikasi. Semua nilai disalin dari hasil gabungan; tidak ada ekstraksi atau perhitungan skor ulang.

## File yang dibaca

- [pairwise_distances.csv](pairwise_distances.csv): empat jarak terpisah; nilai lebih kecil berarti deskriptor lebih dekat.
- [pairwise_similarities.csv](pairwise_similarities.csv): tiga similarity bounded; nilai lebih besar berarti deskriptor lebih dekat. Tidak ada color similarity.
- [pairwise_summary.csv](pairwise_summary.csv): statistik per aplikasi untuk jenis pasangan ini saja; baris `all` sengaja tidak disertakan.
- [investigation_examples.csv](investigation_examples.csv): tiga jarak terendah dan tertinggi untuk setiap deskriptor. Jika nilai seri, urutan mengikuti CSV sumber; daftar ini tidak mencakup semua pasangan yang seri.

## Jumlah pasangan dan rata-rata jarak

| App | Pasangan | Color EMD | Foreground | Edge | Layout |
|---|---:|---:|---:|---:|---:|
| APP01 | 128 | 3.099160 | 0.075751 | 0.007630 | 0.250955 |
| APP02 | 64 | 10.244237 | 0.062019 | 0.017477 | 0.284528 |
| APP03 | 56 | 4.279623 | 0.144719 | 0.010432 | 0.307202 |
| APP04 | 25 | 20.623217 | 0.127687 | 0.009692 | 0.141317 |
| APP05 | 25 | 19.328505 | 0.171116 | 0.004730 | 0.201889 |

Color EMD memiliki satuan berbeda dari tiga jarak lainnya; jangan membandingkan besar angkanya secara langsung atau merata-ratakannya.

## Contoh awal untuk dibuka

| Deskriptor | Pilihan | Screenshot A | Screenshot B | Jarak |
|---|---|---|---|---:|
| color_emd_distance | lowest_distance | [APP02-FLOW01-S015](../../PILOT/screenshots/APP02/FLOW01/S015.png) | [APP02-FLOW02-S00](../../PILOT/screenshots/APP02/FLOW02/S00.png) | 0.000000 |
| color_emd_distance | highest_distance | [APP04-FLOW01-S00](../../PILOT/screenshots/APP04/FLOW01/S00.png) | [APP04-FLOW02-S01](../../PILOT/screenshots/APP04/FLOW02/S01.png) | 55.490974 |
| foreground_distance | lowest_distance | [APP02-FLOW01-S015](../../PILOT/screenshots/APP02/FLOW01/S015.png) | [APP02-FLOW02-S00](../../PILOT/screenshots/APP02/FLOW02/S00.png) | 0.000000 |
| foreground_distance | highest_distance | [APP05-FLOW01-S04](../../PILOT/screenshots/APP05/FLOW01/S04.png) | [APP05-FLOW02-S01](../../PILOT/screenshots/APP05/FLOW02/S01.png) | 0.491528 |
| edge_distance | lowest_distance | [APP02-FLOW01-S015](../../PILOT/screenshots/APP02/FLOW01/S015.png) | [APP02-FLOW02-S00](../../PILOT/screenshots/APP02/FLOW02/S00.png) | 0.000000 |
| edge_distance | highest_distance | [APP02-FLOW01-S013](../../PILOT/screenshots/APP02/FLOW01/S013.png) | [APP02-FLOW02-S03](../../PILOT/screenshots/APP02/FLOW02/S03.png) | 0.078730 |
| layout_distance | lowest_distance | [APP02-FLOW01-S015](../../PILOT/screenshots/APP02/FLOW01/S015.png) | [APP02-FLOW02-S00](../../PILOT/screenshots/APP02/FLOW02/S00.png) | 0.000000 |
| layout_distance | highest_distance | [APP03-FLOW01-S01](../../PILOT/screenshots/APP03/FLOW01/S01.png) | [APP03-FLOW02-S08](../../PILOT/screenshots/APP03/FLOW02/S08.png) | 0.624279 |

## Cara investigasi

1. Pilih satu aplikasi, lalu baca satu deskriptor pada satu waktu. Cocokkan `screen_a`, `screen_b`, `flow_a`, dan `flow_b`.
2. Buka kedua screenshot pada contoh jarak rendah/tinggi. Catat apakah perbedaan terutama berasal dari warna dominan, proporsi konten, teks/edge, atau posisi area.
3. Periksa hasil ekstraksi bila angka tampak tidak sesuai: footer, device chrome, batas pucat, komponen menyatu, dan area kosong di dalam bounding box bisa memengaruhi deskriptor.
4. Catat observasi beserta ID pasangan dan deskriptornya. Jarak rendah tidak otomatis berarti konsisten; jarak tinggi tidak otomatis berarti kesalahan desain.

Dalam folder ini kedua screenshot berasal dari flow berbeda dalam aplikasi yang sama. Perbedaan tujuan layar bisa wajar; flow tidak mengubah skor.

Catatan ini menampilkan statistik dan contoh berdasarkan angka, bukan audit visual baru atau kesimpulan konsistensi. Belum ada skor komposit, threshold, atau uji perbedaan statistik.

Rumus dan asumsi lengkap: [PAIRWISE_METHODS.md](../../PAIRWISE_METHODS.md). Kembali ke [panduan gabungan](../INVESTIGATION.md).
