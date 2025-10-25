import re
import pandas as pd
from typing import Union


def clean_review_text(text: Union[str, float]) -> str:
    """
    Membersihkan teks review dengan berbagai transformasi:
    1. Menghilangkan newline, tab, dan whitespace berlebih
    2. Mengubah ke huruf kecil
    3. Menghilangkan tanda petik ganda
    4. Menghilangkan emoji dan simbol khusus
    5. Menghilangkan URL
    6. Menghilangkan angka yang berdiri sendiri di awal kalimat (numbering)
    7. Menghilangkan whitespace berlebih
    
    Args:
        text: Teks review yang akan dibersihkan
        
    Returns:
        Teks yang sudah dibersihkan
    """
    # Handle missing values
    if pd.isna(text) or text == '':
        return ''
    
    # Convert to string
    text = str(text)
    
    # 1. Menghilangkan URL
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # 2. Menghilangkan emoji dan simbol khusus
    # Pattern untuk emoji (Unicode ranges)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA00-\U0001FA6F"  # chess symbols
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "\U00002700-\U000027BF"
        "]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    
    # 3. Menghilangkan newline dan tab dengan spasi
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('\t', ' ')
    
    # 4. Menghilangkan tanda petik ganda
    text = text.replace('"', '')
    
    # 5. Mengubah ke huruf kecil
    text = text.lower()
    
    # 6. Menghilangkan numbering di awal kalimat (contoh: "1. ", "2. ")
    text = re.sub(r'\b\d+\.\s+', '', text)
    
    # 7. Menghilangkan karakter khusus berlebihan (kecuali tanda baca dasar)
    # Mempertahankan: huruf, angka, spasi, dan tanda baca dasar (.,!?-)
    text = re.sub(r'[^\w\s.,!?\-]', '', text)
    
    # 8. Menghilangkan titik berjejer (contoh: "..." menjadi " ")
    text = re.sub(r'\.{2,}', ' ', text)
    
    # 9. Menghilangkan whitespace berlebih
    text = re.sub(r'\s+', ' ', text)
    
    # 10. Trim whitespace di awal dan akhir
    text = text.strip()
    
    return text


def clean_review_column(df: pd.DataFrame, column_name: str = 'review', inplace: bool = False) -> pd.DataFrame:
    """
    Membersihkan kolom review dalam DataFrame.
    
    Args:
        df: DataFrame yang berisi kolom review
        column_name: Nama kolom yang akan dibersihkan (default: 'review')
        inplace: Jika True, modifikasi DataFrame asli. Jika False, return DataFrame baru
        
    Returns:
        DataFrame dengan kolom review yang sudah dibersihkan
    """
    if not inplace:
        df = df.copy()
    
    if column_name not in df.columns:
        raise ValueError(f"Kolom '{column_name}' tidak ditemukan dalam DataFrame")
    
    # Apply cleaning function
    df[column_name] = df[column_name].apply(clean_review_text)
    
    # Optional: Remove empty reviews after cleaning
    df = df[df[column_name] != '']
    
    return df


def clean_csv_file(input_path: str, output_path: str, review_column: str = 'review'):
    """
    Membaca CSV, membersihkan kolom review, dan menyimpan hasilnya.
    
    Args:
        input_path: Path file CSV input
        output_path: Path file CSV output
        review_column: Nama kolom review yang akan dibersihkan
    """
    # Read CSV
    df = pd.read_csv(input_path)
    
    print(f"Total reviews sebelum cleaning: {len(df)}")
    
    # Clean review column
    df_cleaned = clean_review_column(df, column_name=review_column, inplace=False)
    
    print(f"Total reviews setelah cleaning: {len(df_cleaned)}")
    
    # Save to CSV
    df_cleaned.to_csv(output_path, index=False)
    
    print(f"File berhasil disimpan ke: {output_path}")
    
    return df_cleaned


# Example usage
if __name__ == "__main__":
    # Contoh penggunaan dengan file
    input_file = "dataset/reviews_WIZZMIE_Banyuwangi_20251024_011109.csv"
    output_file = "data_clean/reviews_WIZZMIE_Banyuwangi.csv"
    
    # Clean the CSV file
    df_cleaned = clean_csv_file(input_file, output_file)
    
    # Tampilkan sample hasil cleaning
    print("\n=== Sample Hasil Cleaning ===")
    print(df_cleaned[['username', 'review']].head())
