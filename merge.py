import os
import glob
import pandas as pd

DATASET_DIR = os.path.join(os.path.dirname(__file__), "dataset")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "data_clean", "all_reviews_merged.csv")


def read_review_file(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, engine="python", on_bad_lines="skip")
    except TypeError:
        df = pd.read_csv(path, engine="python")
    cols_map = {c: c.lower().strip() for c in df.columns}
    df.columns = list(cols_map.values())
    review_candidates = [
        "review",
        "ulasan",
        "text",
        "comment",
        "content",
    ]
    place_candidates = [
        "nama_tempat",
        "place",
        "place_name",
        "placename",
        "nama",
        "location",
        "lokasi",
    ]
    review_col = next((c for c in review_candidates if c in df.columns), None)
    place_col = next((c for c in place_candidates if c in df.columns), None)
    if review_col is None or place_col is None:
        return pd.DataFrame(columns=["nama_tempat", "review"])
    out = df[[place_col, review_col]].rename(columns={place_col: "nama_tempat", review_col: "review"})
    return out


def merge_reviews(dataset_dir: str) -> pd.DataFrame:
    pattern = os.path.join(dataset_dir, "**", "*.csv")
    paths = [p for p in glob.glob(pattern, recursive=True) if os.path.basename(p).lower() != "places.csv"]
    frames = []
    for p in paths:
        try:
            part = read_review_file(p)
        except Exception:
            continue
        if not part.empty:
            frames.append(part)
    if not frames:
        return pd.DataFrame(columns=["nama_tempat", "review"])
    all_df = pd.concat(frames, ignore_index=True)
    for col in ["nama_tempat", "review"]:
        if col in all_df.columns:
            all_df[col] = all_df[col].astype(str).str.strip()
    all_df = all_df.replace({"": pd.NA, "nan": pd.NA})
    all_df = all_df.dropna(subset=["nama_tempat", "review"])
    all_df = all_df.drop_duplicates(subset=["nama_tempat", "review"]).reset_index(drop=True)
    return all_df


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    merged = merge_reviews(DATASET_DIR)
    # Pastikan hanya dua kolom yang ditulis
    cols = [c for c in ["nama_tempat", "review"] if c in merged.columns]
    merged[cols].to_csv(OUTPUT_PATH, index=False)


if __name__ == "__main__":
    main()

