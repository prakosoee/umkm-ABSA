import pandas as pd
import os
from pathlib import Path


def merge_cleaned_reviews(input_folder: str = "data_clean", 
                          output_file: str = "data_clean/all_reviews_merged.csv",
                          columns_to_keep: list = ['username', 'review']):
    """
    Merge semua file CSV dari folder data_clean menjadi 1 file.
    Hanya mempertahankan kolom yang ditentukan (default: username dan review).
    
    Args:
        input_folder: Folder yang berisi file CSV yang akan di-merge
        output_file: Path file output hasil merge
        columns_to_keep: List kolom yang akan dipertahankan
    
    Returns:
        DataFrame hasil merge
    """
    # Get all CSV files in the folder
    csv_files = list(Path(input_folder).glob("*.csv"))
    
    # Filter out the merged file if it exists
    csv_files = [f for f in csv_files if f.name != os.path.basename(output_file)]
    
    if not csv_files:
        print(f"Tidak ada file CSV ditemukan di folder '{input_folder}'")
        return None
    
    print(f"Ditemukan {len(csv_files)} file CSV:")
    for file in csv_files:
        print(f"  - {file.name}")
    
    # List to store dataframes
    dfs = []
    
    # Read each CSV and keep only specified columns
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            
            # Check if required columns exist
            missing_cols = [col for col in columns_to_keep if col not in df.columns]
            if missing_cols:
                print(f"⚠️  File {file.name} tidak memiliki kolom: {missing_cols}. Dilewati.")
                continue
            
            # Keep only specified columns
            df_filtered = df[columns_to_keep].copy()
            
            print(f"✓ {file.name}: {len(df_filtered)} reviews")
            dfs.append(df_filtered)
            
        except Exception as e:
            print(f"❌ Error membaca {file.name}: {e}")
            continue
    
    if not dfs:
        print("Tidak ada data yang berhasil dibaca.")
        return None
    
    # Merge all dataframes
    merged_df = pd.concat(dfs, ignore_index=True)
    
    # Remove duplicates (optional)
    original_count = len(merged_df)
    merged_df = merged_df.drop_duplicates(subset=['review'], keep='first')
    duplicates_removed = original_count - len(merged_df)
    
    print(f"\n{'='*50}")
    print(f"Total reviews sebelum merge: {original_count}")
    print(f"Duplikat dihapus: {duplicates_removed}")
    print(f"Total reviews setelah merge: {len(merged_df)}")
    print(f"{'='*50}")
    
    # Save to CSV
    merged_df.to_csv(output_file, index=False)
    print(f"\n✓ File berhasil disimpan ke: {output_file}")
    
    return merged_df


def merge_with_custom_columns(input_folder: str = "data_clean",
                               output_file: str = "data_clean/all_reviews_merged_full.csv",
                               columns_to_keep: list = None):
    """
    Merge dengan opsi custom kolom yang ingin dipertahankan.
    
    Args:
        input_folder: Folder yang berisi file CSV
        output_file: Path file output
        columns_to_keep: List kolom yang akan dipertahankan. Jika None, semua kolom dipertahankan
    """
    csv_files = list(Path(input_folder).glob("*.csv"))
    csv_files = [f for f in csv_files if f.name != os.path.basename(output_file)]
    
    if not csv_files:
        print(f"Tidak ada file CSV ditemukan di folder '{input_folder}'")
        return None
    
    dfs = []
    
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            
            if columns_to_keep:
                # Keep only specified columns if they exist
                available_cols = [col for col in columns_to_keep if col in df.columns]
                df = df[available_cols].copy()
            
            dfs.append(df)
            print(f"✓ {file.name}: {len(df)} rows")
            
        except Exception as e:
            print(f"❌ Error membaca {file.name}: {e}")
            continue
    
    if not dfs:
        return None
    
    merged_df = pd.concat(dfs, ignore_index=True)
    merged_df.to_csv(output_file, index=False)
    
    print(f"\n✓ Total {len(merged_df)} rows disimpan ke: {output_file}")
    
    return merged_df


# Example usage
if __name__ == "__main__":
    # Merge dengan hanya kolom username dan review
    print("=== Merge Data (Username & Review Only) ===\n")
    df_merged = merge_cleaned_reviews(
        input_folder="data_clean",
        output_file="data_clean/all_reviews_merged.csv",
        columns_to_keep=['username', 'review']
    )
    
    # Tampilkan sample hasil
    if df_merged is not None:
        print("\n=== Sample Data (5 baris pertama) ===")
        print(df_merged.head())
        
        print("\n=== Info Dataset ===")
        print(f"Jumlah baris: {len(df_merged)}")
        print(f"Jumlah kolom: {len(df_merged.columns)}")
        print(f"Kolom: {list(df_merged.columns)}")
