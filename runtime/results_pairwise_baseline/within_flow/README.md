# Investigasi hasil within_flow

Terdapat **411 pasangan** dari lima aplikasi. Semua nilai disalin dari hasil gabungan; tidak ada ekstraksi atau perhitungan skor ulang.

## File yang dibaca

- [pairwise_distances.csv](pairwise_distances.csv): empat jarak terpisah; nilai lebih kecil berarti deskriptor lebih dekat.
- [pairwise_similarities.csv](pairwise_similarities.csv): tiga similarity bounded; nilai lebih besar berarti deskriptor lebih dekat. Tidak ada color similarity.
- [pairwise_summary.csv](pairwise_summary.csv): statistik per aplikasi untuk jenis pasangan ini saja; baris `all` sengaja tidak disertakan.
- [investigation_examples.csv](investigation_examples.csv): tiga jarak terendah dan tertinggi untuk setiap deskriptor. Jika nilai seri, urutan mengikuti CSV sumber; daftar ini tidak mencakup semua pasangan yang seri.

## Jumlah pasangan dan rata-rata jarak

| App | Pasangan | Color EMD | Foreground | Edge | Layout |
|---|---:|---:|---:|---:|---:|
| APP01 | 148 | 3.389378 | 0.078057 | 0.009781 | 0.240641 |
| APP02 | 126 | 14.147666 | 0.062252 | 0.024300 | 0.195536 |
| APP03 | 97 | 2.388803 | 0.056103 | 0.009465 | 0.186726 |
| APP04 | 20 | 23.515707 | 0.118164 | 0.010085 | 0.146948 |
| APP05 | 20 | 21.243263 | 0.199031 | 0.004392 | 0.215427 |

Color EMD memiliki satuan berbeda dari tiga jarak lainnya; jangan membandingkan besar angkanya secara langsung atau merata-ratakannya.

## Contoh awal untuk dibuka

| Deskriptor | Pilihan | Screenshot A | Screenshot B | Jarak |
|---|---|---|---|---:|
| color_emd_distance | lowest_distance | [APP03-FLOW02-S07](../../PILOT/screenshots/APP03/FLOW02/S07.png) | [APP03-FLOW02-S08](../../PILOT/screenshots/APP03/FLOW02/S08.png) | 0.048377 |
| color_emd_distance | highest_distance | [APP04-FLOW01-S00](../../PILOT/screenshots/APP04/FLOW01/S00.png) | [APP04-FLOW01-S04](../../PILOT/screenshots/APP04/FLOW01/S04.png) | 55.602798 |
| foreground_distance | lowest_distance | [APP02-FLOW01-S012](../../PILOT/screenshots/APP02/FLOW01/S012.png) | [APP02-FLOW01-S08](../../PILOT/screenshots/APP02/FLOW01/S08.png) | 0.000009 |
| foreground_distance | highest_distance | [APP05-FLOW01-S00](../../PILOT/screenshots/APP05/FLOW01/S00.png) | [APP05-FLOW01-S04](../../PILOT/screenshots/APP05/FLOW01/S04.png) | 0.472046 |
| edge_distance | lowest_distance | [APP01-FLOW02-S00](../../PILOT/screenshots/APP01/FLOW02/S00.png) | [APP01-FLOW02-S05](../../PILOT/screenshots/APP01/FLOW02/S05.png) | 0.000043 |
| edge_distance | highest_distance | [APP02-FLOW01-S013](../../PILOT/screenshots/APP02/FLOW01/S013.png) | [APP02-FLOW01-S05](../../PILOT/screenshots/APP02/FLOW01/S05.png) | 0.092929 |
| layout_distance | lowest_distance | [APP03-FLOW02-S010](../../PILOT/screenshots/APP03/FLOW02/S010.png) | [APP03-FLOW02-S09](../../PILOT/screenshots/APP03/FLOW02/S09.png) | 0.000000 |
| layout_distance | highest_distance | [APP01-FLOW01-S06](../../PILOT/screenshots/APP01/FLOW01/S06.png) | [APP01-FLOW01-S08](../../PILOT/screenshots/APP01/FLOW01/S08.png) | 0.501420 |

## Cara investigasi

1. Pilih satu aplikasi, lalu baca satu deskriptor pada satu waktu. Cocokkan `screen_a`, `screen_b`, `flow_a`, dan `flow_b`.
2. Buka kedua screenshot pada contoh jarak rendah/tinggi. Catat apakah perbedaan terutama berasal dari warna dominan, proporsi konten, teks/edge, atau posisi area.
3. Periksa hasil ekstraksi bila angka tampak tidak sesuai: footer, device chrome, batas pucat, komponen menyatu, dan area kosong di dalam bounding box bisa memengaruhi deskriptor.
4. Catat observasi beserta ID pasangan dan deskriptornya. Jarak rendah tidak otomatis berarti konsisten; jarak tinggi tidak otomatis berarti kesalahan desain.

Dalam folder ini kedua screenshot berasal dari flow yang sama. Tahap atau tujuan layar tetap bisa berbeda.

Catatan ini menampilkan statistik dan contoh berdasarkan angka, bukan audit visual baru atau kesimpulan konsistensi. Belum ada skor komposit, threshold, atau uji perbedaan statistik.

Rumus dan asumsi lengkap: [PAIRWISE_METHODS.md](../../PAIRWISE_METHODS.md). Kembali ke [panduan gabungan](../INVESTIGATION.md).
