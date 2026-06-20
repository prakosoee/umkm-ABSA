from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from datetime import datetime

class GoogleMapsReviewScraper:
    def __init__(self, url, max_reviews=None):
        self.url = url
        self.max_reviews = max_reviews
        self.driver = None
        self.reviews = []
        self.seen_reviews = set()
        
    def setup_driver(self):
        """Inisialisasi Chrome driver dengan opsi anti-deteksi"""
        options = Options()
        options.add_argument("--lang=id")
        options.add_argument("--accept-language=id-ID,id")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.maximize_window()
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("Browser berhasil diinisialisasi")
        
    def get_place_name(self):
        """Ambil nama tempat dari halaman"""
        try:
            wait = WebDriverWait(self.driver, 10)
            nama_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob"))
            )
            nama = nama_element.text.strip()
            print(f"Nama tempat: {nama}")
            return nama
        except Exception as e:
            print(f"Gagal mengambil nama tempat: {e}")
            return "Unknown"
    
    def scroll_to_reviews_section(self):
        """Scroll ke bagian ulasan"""
        try:
            wait = WebDriverWait(self.driver, 10)
            review_section = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb.WNBkOb.XiKgde"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", review_section)
            time.sleep(2)
            print("Berhasil scroll ke section reviews")
            return True
        except Exception as e:
            print(f"Gagal scroll ke section reviews: {e}")
            return False
    
    def click_more_reviews_button(self):
        """Klik tombol 'Ulasan lainnya' atau sejenisnya untuk membuka panel review lengkap"""
        # Coba multiple selector
        selectors = [
            "button.M77dve[aria-label*='Ulasan lainnya']",
            "button.M77dve[aria-label*='ulasan']",
            "button.M77dve[aria-label*='review']",
            "button.M77dve[aria-label*='Review']",
            "button:has(span:contains('Ulasan'))",
            "button[aria-label*='Ulasan']",
            "button[aria-label*='ulasan']",
            "button[aria-label*='review']",
        ]
        for sel in selectors:
            try:
                btn = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
                )
                if btn:
                    btn.click()
                    time.sleep(3)
                    print(f"✓ Berhasil klik tombol review: {sel}")
                    try:
                        panel = self.get_scrollable_element()
                        if panel:
                            self.driver.execute_script("arguments[0].scrollBy(0, 1000);", panel)
                            time.sleep(1)
                    except Exception:
                        pass
                    return True
            except Exception:
                continue
        print("⚠ Tidak ada tombol review terpisah — mungkin panel review sudah terlihat langsung")
        return False
    
    def expand_review_text(self, review_container):
        """Klik tombol 'Lainnya' untuk melihat teks review lengkap"""
        try:
            more_button = review_container.find_element(By.CSS_SELECTOR, "button.w8nwRe.kyuRq")
            if more_button.is_displayed():
                # Scroll ke button dulu
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_button)
                time.sleep(0.2)
                self.driver.execute_script("arguments[0].click();", more_button)
                time.sleep(0.3)
                return True
        except NoSuchElementException:
            return False
        except Exception:
            return False
    
    def extract_review_data(self, container, nama_tempat):
        """Extract data dari satu container review"""
        try:
            # Username
            try:
                user_element = container.find_element(By.CSS_SELECTOR, "div.d4r55")
                username = user_element.text.strip()
            except NoSuchElementException:
                username = "Unknown"
            
            # Rating
            try:
                rating_element = container.find_element(By.CSS_SELECTOR, "span.kvMYJc")
                rating_text = rating_element.get_attribute("aria-label")
                rating = rating_text.split()[0] if rating_text else "Unknown"
            except NoSuchElementException:
                rating = "Unknown"
            
            # Expand review text jika ada tombol "Lainnya"
            self.expand_review_text(container)
            
            # Review text
            try:
                review_element = container.find_element(By.CSS_SELECTOR, "span.wiI7pd")
                review_text = review_element.text.strip()
            except NoSuchElementException:
                review_text = ""
            
            # Validasi data
            if not review_text or not username:
                return None
            
            # Cek duplikasi
            review_key = (username, review_text[:100])
            if review_key in self.seen_reviews:
                return None
            
            self.seen_reviews.add(review_key)
            
            return {
                "nama_tempat": nama_tempat,
                "username": username,
                "rating": rating,
                "review": review_text
            }
            
        except Exception:
            return None
    
    def get_scrollable_element(self):
        """Dapatkan elemen yang bisa di-scroll"""
        selectors = [
            "div.m6QErb.DxyBCb.dS8AEf.XiKgde",
            "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde",
            "div.m6QErb.XiKgde.P9tVlf.dS8AEf",
            "div.m6QErb.DxyBCb.dS8AEf",
            "div.m6QErb.DxyBCb",
            "div.m6QErb.XiKgde",
        ]

        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    print(f"Menemukan scrollable element dengan selector: {selector}")
                    return element
            except NoSuchElementException:
                continue
        return None
    
    def scroll_review_panel(self, scroll_element, scroll_amount=3000):
        """Scroll di dalam panel review dengan berbagai metode"""
        if not scroll_element:
            return False
        
        try:
            # Ambil scroll position sebelum scroll
            scroll_top_before = self.driver.execute_script("return arguments[0].scrollTop", scroll_element)
            
            # Scroll dengan amount tertentu (bukan langsung ke bottom)
            self.driver.execute_script(f"arguments[0].scrollBy(0, {scroll_amount})", scroll_element)
            time.sleep(1.5)
            
            # Cek apakah posisi scroll berubah
            scroll_top_after = self.driver.execute_script("return arguments[0].scrollTop", scroll_element)
            
            return scroll_top_after > scroll_top_before
            
        except Exception:
            print("Error saat scroll")
            
            # Method 2: Fallback dengan send keys
            try:
                scroll_element.send_keys(Keys.PAGE_DOWN)
                time.sleep(1)
                return True
            except Exception:
                return False
    
    def hide_image_elements(self):
        """Sembunyikan element gambar yang menghalangi"""
        try:
            # Sembunyikan semua button gambar
            self.driver.execute_script("""
                var imageButtons = document.querySelectorAll('button.Tya61d');
                imageButtons.forEach(function(btn) {
                    btn.style.display = 'none';
                });
            """)
            print("✓ Element gambar disembunyikan")
        except Exception as e:
            print(f"⚠ Gagal menyembunyikan gambar: {e}")

    def hide_gakpenting_elements(self):
        """Sembunyikan element yang tidak penting"""
        try:
            # Sembunyikan elemen tidak penting (div[jslog="127691"] dan beberapa kelas tambahan)
            self.driver.execute_script("""
                var selectors = [
                    'div[jslog="127691"]',
                    'div.nUH3Jc',
                    'div.vyucnb',
                    'div.PPCwl',
                    'div.AyRUI',
                    'div.m6QErb.Hk4XGb.QoaCgb.XiKgde.KoSBEe.tLjsW',
                    'div.m6QErb.Pf6ghf.XiKgde.KoSBEe.ecceSd.tLjsW',
                    'div.m6QErb.XiKgde.tLjsW'
                ].join(',');
                var gakpenting = document.querySelectorAll(selectors);
                gakpenting.forEach(function(el){ el.style.display = 'none'; });
            """)
            print("✓ Element gakpenting disembunyikan")
        except Exception as e:
            print(f"⚠ Gagal menyembunyikan gakpenting: {e}")
    
    def wait_for_reviews_to_load(self):
        """Tunggu sampai review containers muncul"""
        selectors = ["div.jftiEf", "div.JTuXWc", "div[data-review-id]", "div[role='article']"]
        max_wait = 15
        wait_interval = 0.5
        elapsed = 0

        while elapsed < max_wait:
            for sel in selectors:
                try:
                    containers = self.driver.find_elements(By.CSS_SELECTOR, sel)
                    if len(containers) > 0:
                        print(f"✓ Ditemukan {len(containers)} review containers dengan selector: {sel}")
                        return containers
                except Exception:
                    pass

            time.sleep(wait_interval)
            elapsed += wait_interval

        return []
    
    def scrape_reviews(self):
        """Main function untuk scraping reviews"""
        try:
            # Setup driver
            self.setup_driver()
            
            # Buka URL
            print("\n⟳ Membuka URL...")
            self.driver.get(self.url)
            time.sleep(5)
            
            # Ambil nama tempat
            nama_tempat = self.get_place_name()
            
            # Scroll ke section reviews
            if not self.scroll_to_reviews_section():
                print("✗ Gagal menemukan section reviews")
                return []
            
            # Klik tombol "Ulasan lainnya" — skip jika tidak ada
            self.click_more_reviews_button()
            
            print(f"\n⟳ Mulai scraping reviews (Target: {self.max_reviews if self.max_reviews else 'Semua'})")
            
            # Dapatkan elemen yang bisa di-scroll
            scroll_element = self.get_scrollable_element()
            if not scroll_element:
                print("✗ Tidak dapat menemukan elemen scrollable")
                return []
            
            print("✓ Elemen scrollable ditemukan")
            
            # Sembunyikan element yang menghalangi
            self.hide_image_elements()
            self.hide_gakpenting_elements()

            # INFINITE SCROLL: muat semua containers terlebih dahulu
            print("\n⟳ Infinite scroll hingga mencapai target containers...")
            target = self.max_reviews if self.max_reviews else None
            seen_count = 0
            scroll_attempts = 0
            stagnant_streak = 0
            max_stagnant = 8
            max_attempts = 300

            # Cari review container dengan beberapa selector
            def find_review_containers():
                for sel in ["div.jftiEf", "div.JTuXWc", "div[data-review-id]", "div[role='article']"]:
                    els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                    if els:
                        return els
                return []

            while True:
                containers = find_review_containers()
                current_count = len(containers)

                if current_count > seen_count:
                    seen_count = current_count
                    stagnant_streak = 0
                else:
                    stagnant_streak += 1

                if target and current_count >= target:
                    print(f"✓ Target containers tercapai: {current_count}/{target}")
                    break

                if stagnant_streak >= max_stagnant:
                    print(f"⚠ Stagnan {stagnant_streak} langkah, berhenti scroll. Total containers: {current_count}")
                    break

                if scroll_attempts >= max_attempts:
                    print(f"⚠ Mencapai batas scroll: {max_attempts}")
                    break

                # Scroll bertahap
                self.scroll_review_panel(scroll_element, scroll_amount=1800)
                scroll_attempts += 1

                # Sembunyikan elemen periodik untuk kelancaran
                if scroll_attempts % 4 == 0:
                    self.hide_image_elements()
                    self.hide_gakpenting_elements()

                # Report progress berkala
                if scroll_attempts % 10 == 0:
                    print(f"  📊 Containers: {current_count} | Scroll: {scroll_attempts}")

            print(f"✓ Selesai scroll. Total containers termuat: {seen_count}")

            # EXTRACT SEKALI DI AKHIR
            print("\n⟳ Mulai extract data sekali jalan...")
            final_containers = find_review_containers()
            extracted = 0
            for container in final_containers:
                if self.max_reviews and len(self.reviews) >= self.max_reviews:
                    break
                data = self.extract_review_data(container, nama_tempat)
                if data:
                    self.reviews.append(data)
                    extracted += 1
            print(f"✓ Extract selesai. Didapat: {extracted} records")
            print(f"\n✓ Scraping selesai! Total: {len(self.reviews)} reviews")
            print(f"  Total scroll attempts: {scroll_attempts}")
            return self.reviews
            
        except Exception as e:
            print(f"\n✗ Error fatal: {e}")
            import traceback
            traceback.print_exc()
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
                print("✓ Browser ditutup")
    
    def save_to_csv(self, filename=None):
        """Simpan hasil scraping ke CSV"""
        if not self.reviews:
            print("✗ Tidak ada data untuk disimpan")
            return False
        
        try:
            df = pd.DataFrame(self.reviews)
            
            # Generate filename jika tidak disediakan
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nama_tempat = self.reviews[0]['nama_tempat'].replace(" ", "_")[:30]
                filename = f"dataset/reviews_{nama_tempat}_{timestamp}.csv"
            
            # Pastikan folder dataset ada
            import os
            os.makedirs("dataset", exist_ok=True)
            
            # Simpan ke CSV
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n✓ Data berhasil disimpan ke: {filename}")
            
            # Tampilkan statistik
            print("\n📊 Statistik:")
            print(f"  • Total reviews: {len(df)}")
            ratings = df[df['rating'] != 'Unknown']['rating'].astype(float)
            if len(ratings) > 0:
                print(f"  • Rating rata-rata: {ratings.mean():.2f}")
            
            print("\n📋 Preview data (5 pertama):")
            for i, row in df.head(5).iterrows():
                print(f"\n  {i+1}. {row['username']}")
                print(f"     Rating: {row['rating']} ⭐")
                print(f"     Review: {row['review'][:100]}...")
            
            return True
            
        except Exception as e:
            print(f"✗ Error saat menyimpan: {e}")
            return False


def scrape_batch_from_links(csv_file, max_reviews=None, delay_between=2, output_dir=None):
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"✗ Gagal membaca file: {e}")
        return
    if 'link' not in df.columns:
        print("✗ Kolom 'link' tidak ditemukan pada file input")
        return
    total = len(df)
    print(f"⟳ Mulai batch scraping: {total} link")
    # Siapkan folder output jika diberikan
    if output_dir:
        import os
        os.makedirs(output_dir, exist_ok=True)
    import re
    from datetime import datetime
    for i, row in df.iterrows():
        url = str(row['link']).strip()
        if not url or url.lower() == 'nan':
            continue
        print(f"\n[{i+1}/{total}] Scraping: {url}")
        scraper = GoogleMapsReviewScraper(url=url, max_reviews=max_reviews)
        reviews = scraper.scrape_reviews()
        if reviews:
            # Simpan ke file pada output_dir jika disediakan
            if output_dir:
                try:
                    place_name = scraper.reviews[0]['nama_tempat'] if scraper.reviews else 'unknown'
                    safe_place = re.sub(r"\W+", "_", str(place_name)).strip("_")[:50]
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = os.path.join(output_dir, f"reviews_{safe_place}_{ts}.csv")
                    scraper.save_to_csv(filename=filename)
                except Exception:
                    # fallback default
                    scraper.save_to_csv()
            else:
                scraper.save_to_csv()
        else:
            print("✗ Tidak ada review untuk disimpan pada link ini")
        time.sleep(delay_between)

# ===== CARA PENGGUNAAN =====
if __name__ == "__main__":
    gmaps_url = "https://maps.app.goo.gl/TjQhU4PwAUzQZ2xN8"

    scraper = GoogleMapsReviewScraper(url=gmaps_url, max_reviews=500)
    reviews = scraper.scrape_reviews()

    if reviews:
        scraper.save_to_csv()
    else:
        print("✗ Tidak ada review yang berhasil diambil")