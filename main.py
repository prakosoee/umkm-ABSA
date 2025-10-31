import argparse
from scrap_link import GoogleMapsSearchScraper
from scrapping import scrape_batch_from_links

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, required=True)
    parser.add_argument("--max-tempat", type=int, default=50)
    parser.add_argument("--max-review-per-tempat", type=int, default=None)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--places-output", type=str, default=None)
    parser.add_argument("--output-dir", type=str, required=True, help="Nama folder output di bawah folder dataset/")
    args = parser.parse_args()

    # Siapkan folder output di bawah dataset
    import os
    base_dir = os.path.join("dataset", args.output_dir)
    os.makedirs(base_dir, exist_ok=True)

    place_scraper = GoogleMapsSearchScraper(
        query=args.query,
        max_places=args.max_tempat,
        headless=args.headless,
    )
    places = place_scraper.scrape()
    if not places:
        return
    # Simpan daftar tempat ke folder output; jika user memberi places-output, hormati path itu
    places_csv = args.places_output if args.places_output else os.path.join(base_dir, "places.csv")
    places_csv = place_scraper.save_to_csv(filename=places_csv)

    scrape_batch_from_links(
        csv_file=places_csv,
        max_reviews=args.max_review_per_tempat,
        delay_between=args.delay,
        output_dir=base_dir,
    )

if __name__ == "__main__":
    main()
