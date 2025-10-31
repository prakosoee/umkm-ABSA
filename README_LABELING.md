# Aspect-Based Sentiment Analysis - Data Labeling

## Overview
Script untuk melabeli dataset review restoran dengan **Aspect-Based Sentiment Analysis (ABSA)**. Setiap review akan dilabeli untuk 5 aspek berbeda dengan sentimen positive/negative/neutral.

## Aspek yang Dilabeli

1. **food_quality** (Kualitas Makanan)
   - Rasa, tekstur, kesegaran makanan
   
2. **price** (Harga)
   - Keterjangkauan, value for money
   
3. **service** (Pelayanan)
   - Keramahan, kecepatan, responsivitas staff
   
4. **ambiance** (Suasana)
   - Kenyamanan tempat, kebersihan, fasilitas
   
5. **portion** (Porsi)
   - Ukuran porsi, kecukupan makanan

## Format Output

```csv
sentence,username,food_quality,price,service,ambiance,portion
"bakso enak, harga murah",User1,positive,positive,neutral,neutral,neutral
"pelayanan lambat tapi makanan enak",User2,positive,neutral,negative,neutral,neutral
```

## Cara Penggunaan

### 1. Install Dependencies
```bash
pip install pandas transformers torch
```

### 2. Jalankan Script
```bash
python make_labels.py
```

### 3. Pilih Mode

#### Mode 1: Auto-label Semua Data
- Melabeli semua review di `data_clean/all_reviews_merged.csv`
- Menggunakan keyword-based approach
- Cepat dan otomatis
- Akurasi ~70-80% (perlu manual review untuk hasil optimal)

#### Mode 2: Auto-label Sample Data
- Melabeli sejumlah sample tertentu
- Cocok untuk testing atau membuat dataset kecil
- Bisa pilih jumlah sample yang diinginkan

#### Mode 3: Manual Review Labels
- Review dan edit label yang sudah dibuat
- Interaktif - review satu per satu
- Auto-save setiap 10 reviews
- Instruksi:
  - **Enter**: Keep label saat ini
  - **p**: Ubah ke positive
  - **n**: Ubah ke negative
  - **neu**: Ubah ke neutral
  - **q**: Quit dan save progress

## Keyword-Based Approach

Script menggunakan keyword dictionary untuk setiap aspek:

### Food Quality Keywords
- **Positive**: enak, lezat, mantap, nikmat, gurih, empuk, recommended, dll
- **Negative**: hambar, tawar, tidak enak, lembek, alot, mengecewakan, dll

### Price Keywords
- **Positive**: murah, terjangkau, worth it, masuk kantong, dll
- **Negative**: mahal, kemahalan, overprice, tidak sesuai, dll

### Service Keywords
- **Positive**: ramah, baik, cepat, sopan, membantu, dll
- **Negative**: lambat, lama, ketus, jutek, tidak ramah, dll

### Ambiance Keywords
- **Positive**: nyaman, bersih, rapi, cozy, sejuk, ber-ac, dll
- **Negative**: kotor, sempit, panas, gerah, tidak nyaman, dll

### Portion Keywords
- **Positive**: banyak, besar, jumbo, mengenyangkan, dll
- **Negative**: sedikit, kecil, kurang, mengecil, dll

## Workflow Rekomendasi

1. **Auto-label** semua data dengan Mode 1
2. **Review statistik** distribusi label
3. **Manual review** sample data (100-200 reviews) dengan Mode 3
4. **Evaluasi akurasi** keyword-based approach
5. **Tambah/edit keywords** jika perlu
6. **Re-run** auto-labeling dengan keywords yang sudah diperbaiki

## Upgrade ke BERT Model

Untuk hasil lebih akurat, Anda bisa:

1. **Fine-tune BERT model** dengan data yang sudah dilabeli manual
2. **Gunakan model** untuk auto-labeling data baru
3. **Script sudah siap** untuk integrasi BERT (set `use_bert=True`)

### Contoh Fine-tuning BERT
```python
# TODO: Implementasi fine-tuning
# 1. Load labeled data
# 2. Split train/validation
# 3. Fine-tune indobert-base-p2
# 4. Save model
# 5. Use untuk labeling otomatis
```

## Output Files

- **data_training/labeled_reviews.csv**: Dataset yang sudah dilabeli
- Berisi kolom: `sentence`, `username`, `food_quality`, `price`, `service`, `ambiance`, `portion`

## Tips

1. **Mulai dengan sample kecil** untuk testing
2. **Review manual** sangat disarankan untuk data training
3. **Tambahkan keywords** yang spesifik untuk domain Anda
4. **Gunakan Mode 3** untuk quality control
5. **Save progress** secara berkala

## Troubleshooting

### Import Error: transformers
```bash
pip install transformers torch
```

### File Not Found
Pastikan file `data_clean/all_reviews_merged.csv` ada. Jalankan `merge_data.py` terlebih dahulu.

### Folder data_training tidak ada
Script akan membuat folder otomatis, atau buat manual:
```bash
mkdir data_training
```

## Next Steps

Setelah data dilabeli:
1. Split data menjadi train/validation/test
2. Fine-tune BERT model untuk ABSA
3. Evaluasi model performance
4. Deploy model untuk production
