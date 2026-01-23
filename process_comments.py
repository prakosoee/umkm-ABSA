import csv
import re
import string
import os
import math

def clean_text(text):
    # Remove digits
    text = re.sub(r'\d+', '', text)
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Normalize whitespace
    text = ' '.join(text.split())
    return text

def main():
    input_file = 'data_ig/result_a.csv'
    output_dir = 'data_ig'
    chunk_size = 50
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return

    comments = []
    
    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if 'comment_text' not in reader.fieldnames:
                print("Error: Column 'comment_text' not found in CSV.")
                return
            
            for row in reader:
                original_text = row['comment_text']
                cleaned_text = clean_text(original_text)
                if cleaned_text: # Only add if not empty after cleaning
                    comments.append(cleaned_text)
                    
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print(f"Total comments processed: {len(comments)}")

    # Split and save
    num_chunks = math.ceil(len(comments) / chunk_size)
    
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size
        chunk = comments[start_idx:end_idx]
        
        output_filename = f"result_a_split_{i+1}.csv"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            with open(output_path, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['comment_text']) # Header
                for comment in chunk:
                    writer.writerow([comment])
            print(f"Saved {output_path} with {len(chunk)} rows.")
        except Exception as e:
             print(f"Error writing to {output_path}: {e}")

if __name__ == "__main__":
    main()
