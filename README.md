# Google Maps Review Scraper & ABSA Labeling

Project untuk scraping review dari Google Maps dan melakukan Aspect-Based Sentiment Analysis (ABSA) labeling untuk data training.

## 📋 Fitur

1. **Web Scraping** - Scraping review dari Google Maps
2. **Data Cleaning** - Membersihkan teks review (remove emoji, normalize text, dll)
3. **Data Merging** - Menggabungkan multiple CSV files
4. **Auto Labeling** - Labeling otomatis dengan keyword-based approach
5. **Manual Review** - Interface untuk review dan koreksi label
6. **Dataset Analysis** - Analisis kelayakan dataset untuk training

## 🚀 Quick Start

### 1. Install Dependencies

**Full Installation** (termasuk BERT & web scraping):
```bash
pip install -r requirements.txt
```

**Minimal Installation** (hanya untuk cleaning & labeling):
```bash
pip install -r requirements-minimal.txt
```

### 2. Workflow

#### A. Orchestrator: Places + Reviews (Recommended)

Gunakan `main.py` untuk menjalankan dua tahap otomatis: ambil daftar tempat (links) lalu scrape reviews per link.

```bash
python main.py \
  --query "geprek kak rose malang" \
  --max-tempat 30 \
  --max-review-per-tempat 200 \
  --output-dir "geprek_kak_rose_run1" \
  [--headless] \
  [--delay 2.0] \
  [--places-output "dataset/geprek_kak_rose_run1/places_custom.csv"]
```

Argumen:
- `--query` (wajib): kata kunci pencarian di Google Maps.
- `--max-tempat` (default 50): jumlah tempat maksimum yang diambil dari hasil pencarian.
- `--max-review-per-tempat` (opsional): batas jumlah review per tempat saat scraping ulasan.
- `--output-dir` (wajib): nama folder tujuan di bawah `dataset/` untuk menyimpan hasil run ini.
- `--headless` (opsional): jalankan Chrome tanpa UI.
- `--delay` (default 2.0): jeda antar scraping link saat mengambil review.
- `--places-output` (opsional): path file CSV untuk daftar tempat; jika tidak diisi, otomatis `dataset/<output-dir>/places.csv`.

Struktur output contoh:
```
dataset/
└── geprek_kak_rose_run1/
    ├── places.csv                  # daftar tempat (name, link, lat, lng, ...)
    ├── reviews_Geprek_Kak_Rose_....csv
    ├── reviews_Geprek_Kak_Rose_....csv
    └── ... (satu file per link yang memiliki review)
```

#### B. Scraping Reviews (Optional)
```bash
python scrapping.py
```
Output: `dataset/reviews_[nama_tempat]_[timestamp].csv`

#### B. Cleaning Reviews
```bash
python cleaning.py
```
- Menghilangkan emoji, newline, tab
- Normalize ke lowercase
- Remove special characters
- Output: `data_clean/reviews_cleaned.csv`

#### C. Merge Multiple Files
```bash
python merge_data.py
```
- Merge semua CSV di folder `data_clean`
- Remove duplicates
- Output: `data_clean/all_reviews_merged.csv`

#### D. Analyze Dataset
```bash
python analyze_dataset.py
```
- Analisis panjang review
- Estimasi token count untuk BERT
- Statistik distribusi
- Output: `data_training/dataset_analysis.csv`

#### E. Label Dataset
```bash
python make_labels.py
```
Mode:
1. **Auto-label semua data** - Keyword-based labeling
2. **Auto-label sample** - Label sejumlah sample tertentu
3. **Manual review** - Review dan edit label interaktif

Output: `data_training/labeled_reviews.csv`

## 📁 Struktur Project

```
gmaps-scraper/
├── scrapping.py              # Web scraping script
├── cleaning.py               # Data cleaning functions
├── merge_data.py             # Merge multiple CSV files
├── analyze_dataset.py        # Dataset analysis
├── make_labels.py            # ABSA labeling tool
├── requirements.txt          # Full dependencies
├── requirements-minimal.txt  # Minimal dependencies
├── README.md                 # This file
├── README_LABELING.md        # Detailed labeling guide
│
├── dataset/                  # Raw scraped data
│   └── reviews_*.csv
│
├── data_clean/              # Cleaned data
│   ├── reviews_*.csv
│   └── all_reviews_merged.csv
│
└── data_training/           # Labeled training data
    ├── labeled_reviews.csv
    └── dataset_analysis.csv
```

## 🏷️ Aspect-Based Sentiment Analysis (ABSA)

Dataset dilabeli untuk 5 aspek dengan 3 sentimen (positive/negative/neutral):

### Aspek:
1. **food_quality** - Kualitas makanan (rasa, tekstur, kesegaran)
2. **price** - Harga (keterjangkauan, value for money)
3. **service** - Pelayanan (keramahan, kecepatan staff)
4. **ambiance** - Suasana (kenyamanan, kebersihan tempat)
5. **portion** - Porsi (ukuran, kecukupan makanan)

### Format Output:
```csv
sentence,username,food_quality,price,service,ambiance,portion
"bakso enak, harga murah",User1,positive,positive,neutral,neutral,neutral
```

## 📊 Dataset Statistics

Berdasarkan analisis terakhir:
- **Total reviews**: 1,874
- **Panjang rata-rata**: 127 karakter / 20 kata
- **Max length**: 1,852 karakter / 296 kata
- **Token estimate**: Max 414 tokens (< 512 BERT limit) ✓
- **Status**: COCOK untuk training BERT

## 🔧 Scripts Detail

### cleaning.py
```python
from cleaning import clean_review_text, clean_csv_file

# Clean single text
clean_text = clean_review_text("Review dengan emoji 😅")

# Clean entire CSV
clean_csv_file("input.csv", "output.csv")
```

### merge_data.py
```python
from merge_data import merge_cleaned_reviews

# Merge all CSV in folder
df = merge_cleaned_reviews(
    input_folder="data_clean",
    output_file="data_clean/merged.csv",
    columns_to_keep=['username', 'review']
)
```

## 📄 License

MIT License

## 👤 Author

Your Name / Team Name

---

**Happy Labeling! 🚀**
