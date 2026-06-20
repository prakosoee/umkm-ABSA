import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import os

def split_dataset_balanced(input_path, output_dir='dataset', train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, random_state=42):
    """
    Split dataset into train/validation/test with balanced score distribution.
    
    Args:
        input_path: Path to input CSV file
        output_dir: Directory to save split files
        train_ratio: Proportion for training set (default 0.7)
        val_ratio: Proportion for validation set (default 0.15)
        test_ratio: Proportion for test set (default 0.15)
        random_state: Random seed for reproducibility
    """
    
    # Load dataset
    df = pd.read_csv(input_path)
    print(f"Total samples: {len(df)}")
    print(f"Score distribution:")
    print(df['score'].value_counts().sort_index())
    print()
    
    # Group by score for stratified splitting
    grouped = df.groupby('score')
    
    train_dfs = []
    val_dfs = []
    test_dfs = []
    
    for score, group in grouped:
        print(f"Processing score {score} ({len(group)} samples)")
        
        # Calculate split sizes
        n_total = len(group)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)
        n_test = n_total - n_train - n_val
        
        # Split within each score group
        if n_total > 1:
            # First split: separate test set
            temp_df, test_df = train_test_split(
                group, 
                test_size=test_ratio, 
                random_state=random_state,
                shuffle=True
            )
            
            # Second split: separate train and validation from remaining
            val_size_adjusted = val_ratio / (train_ratio + val_ratio)
            train_df, val_df = train_test_split(
                temp_df,
                test_size=val_size_adjusted,
                random_state=random_state,
                shuffle=True
            )
        else:
            # If only 1 sample, put it in train
            train_df = group
            val_df = pd.DataFrame()
            test_df = pd.DataFrame()
        
        train_dfs.append(train_df)
        val_dfs.append(val_df)
        test_dfs.append(test_df)
        
        print(f"  - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    
    # Combine all groups
    train_final = pd.concat(train_dfs, ignore_index=True)
    val_final = pd.concat(val_dfs, ignore_index=True)
    test_final = pd.concat(test_dfs, ignore_index=True)
    
    # Shuffle final datasets
    train_final = train_final.sample(frac=1, random_state=random_state).reset_index(drop=True)
    val_final = val_final.sample(frac=1, random_state=random_state).reset_index(drop=True)
    test_final = test_final.sample(frac=1, random_state=random_state).reset_index(drop=True)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save datasets
    train_path = os.path.join(output_dir, 'train.csv')
    val_path = os.path.join(output_dir, 'validation.csv')
    test_path = os.path.join(output_dir, 'test.csv')
    
    train_final.to_csv(train_path, index=False)
    val_final.to_csv(val_path, index=False)
    test_final.to_csv(test_path, index=False)
    
    # Print final statistics
    print(f"\nFinal split results:")
    print(f"Train: {len(train_final)} samples ({len(train_final)/len(df)*100:.1f}%)")
    print(f"Validation: {len(val_final)} samples ({len(val_final)/len(df)*100:.1f}%)")
    print(f"Test: {len(test_final)} samples ({len(test_final)/len(df)*100:.1f}%)")
    
    print(f"\nScore distribution in splits:")
    print("\nTrain:")
    print(train_final['score'].value_counts().sort_index())
    print("\nValidation:")
    print(val_final['score'].value_counts().sort_index())
    print("\nTest:")
    print(test_final['score'].value_counts().sort_index())
    
    print(f"\nFiles saved to:")
    print(f"- {train_path}")
    print(f"- {val_path}")
    print(f"- {test_path}")
    
    return train_final, val_final, test_final

if __name__ == "__main__":
    # Split the dataset
    input_file = 'dataset/dataset-ASAS-cleaned.csv'
    train_df, val_df, test_df = split_dataset_balanced(input_file)
