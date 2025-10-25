from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
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
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✓ Browser berhasil diinisialisasi")
        
    def get_place_name(self):
        """Ambil nama tempat dari halaman"""
        try:
            wait = WebDriverWait(self.driver, 10)
            nama_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob"))
            )
            nama = nama_element.text.strip()
            print(f"✓ Nama tempat: {nama}")
            return nama
        except Exception as e:
            print(f"✗ Gagal mengambil nama tempat: {e}")
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
            print("✓ Berhasil scroll ke section reviews")
            return True
        except Exception as e:
            print(f"✗ Gagal scroll ke section reviews: {e}")
            return False
    
    def click_more_reviews_button(self):
        """Klik tombol 'Ulasan lainnya' untuk membuka panel review lengkap"""
        try:
            wait = WebDriverWait(self.driver, 10)
            more_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.M77dve[aria-label*='Ulasan lainnya']"))
            )
            more_button.click()
            time.sleep(3)
            print("✓ Berhasil klik tombol 'Ulasan lainnya'")
            
            # Tunggu panel baru muncul dengan explicit wait
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb.DxyBCb.dS8AEf.XiKgde"))
            )
            time.sleep(2)
            print("✓ Panel review lengkap berhasil dimuat")
            return True
        except Exception as e:
            print(f"✗ Gagal klik tombol 'Ulasan lainnya': {e}")
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
            except:
                username = "Unknown"
            
            # Rating
            try:
                rating_element = container.find_element(By.CSS_SELECTOR, "span.kvMYJc")
                rating_text = rating_element.get_attribute("aria-label")
                rating = rating_text.split()[0] if rating_text else "Unknown"
            except:
                rating = "Unknown"
            
            # Expand review text jika ada tombol "Lainnya"
            self.expand_review_text(container)
            
            # Review text
            try:
                review_element = container.find_element(By.CSS_SELECTOR, "span.wiI7pd")
                review_text = review_element.text.strip()
            except:
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
            
        except Exception as e:
            return None
    
    def get_scrollable_element(self):
        """Dapatkan elemen yang bisa di-scroll"""
        selectors = [
            "div.m6QErb.DxyBCb.dS8AEf.XiKgde",  # Panel review utama (tanpa kA9KIf)
            "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde",  # Variasi dengan kA9KIf
            "div.m6QErb.DxyBCb.dS8AEf",
            "div.m6QErb.DxyBCb"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    print(f"✓ Menemukan scrollable element dengan selector: {selector}")
                    return element
            except:
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
            
        except Exception as e:
            print(f"✗ Error saat scroll: {e}")
            
            # Method 2: Fallback dengan send keys
            try:
                scroll_element.send_keys(Keys.PAGE_DOWN)
                time.sleep(1)
                return True
            except:
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
        max_wait = 15
        wait_interval = 0.5
        elapsed = 0
        
        while elapsed < max_wait:
            try:
                containers = self.driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
                if len(containers) > 0:
                    print(f"✓ Ditemukan {len(containers)} review containers")
                    return containers
            except:
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
            print(f"\n⟳ Membuka URL...")
            self.driver.get(self.url)
            time.sleep(5)
            
            # Ambil nama tempat
            nama_tempat = self.get_place_name()
            
            # Scroll ke section reviews
            if not self.scroll_to_reviews_section():
                print("✗ Gagal menemukan section reviews")
                return []
            
            # Klik tombol "Ulasan lainnya"
            if not self.click_more_reviews_button():
                print("✗ Gagal membuka panel reviews lengkap")
                return []
            
            print(f"\n⟳ Mulai scraping reviews (Target: {self.max_reviews if self.max_reviews else 'Semua'})")
            
            # Dapatkan elemen yang bisa di-scroll
            scroll_element = self.get_scrollable_element()
            if not scroll_element:
                print("✗ Tidak dapat menemukan elemen scrollable")
                return []
            
            print("✓ Elemen scrollable ditemukan")
            
            # Sembunyikan element gambar yang menghalangi
            self.hide_image_elements()
            # Sembunyikan elemen tidak penting setelah gambar
            self.hide_gakpenting_elements()
            
            # FASE 1: SCROLL DULU untuk load banyak review (tanpa extract data)
            print("\n⟳ FASE 1: Pre-loading reviews dengan scroll...")
            initial_scroll_count = 15  # Scroll 15x dulu untuk load data
            
            for i in range(initial_scroll_count):
                print(f"  Pre-scroll {i+1}/{initial_scroll_count}...")
                self.scroll_review_panel(scroll_element, scroll_amount=2000)
                time.sleep(1)
                
                # Sembunyikan gambar lagi jika muncul
                if i % 5 == 0:
                    self.hide_image_elements()
                    self.hide_gakpenting_elements()
            
            print(f"✓ Pre-loading selesai, mulai extract data...\n")
            
            # Tunggu review containers muncul
            initial_containers = self.wait_for_reviews_to_load()
            if not initial_containers:
                print("✗ Tidak ada review containers yang ditemukan")
                return []
            
            # Reset scroll ke atas untuk mulai extract dari awal
            self.driver.execute_script("arguments[0].scrollTop = 0", scroll_element)
            time.sleep(2)
            print("✓ Kembali ke atas untuk mulai extract data\n")
            
            # FASE 2: EXTRACT DATA sambil scroll
            print("⟳ FASE 2: Extracting review data...")
            
            scroll_attempts = 0
            max_scroll_attempts = 100
            no_new_reviews_streak = 0
            max_no_new_streak = 5
            
            while scroll_attempts < max_scroll_attempts:
                # Cek apakah sudah mencapai target
                if self.max_reviews and len(self.reviews) >= self.max_reviews:
                    print(f"\n✓ Target {self.max_reviews} reviews tercapai!")
                    break
                
                # Jika tidak ada review baru dalam beberapa scroll, hentikan
                if no_new_reviews_streak >= max_no_new_streak:
                    print(f"\n⚠ Tidak ada review baru setelah {max_no_new_streak} kali scroll, menghentikan...")
                    break
                
                # Ambil semua container review yang ada saat ini
                review_containers = self.driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
                
                if not review_containers:
                    print(f"  ⚠ Tidak ada containers di scroll ke-{scroll_attempts + 1}")
                    scroll_attempts += 1
                    time.sleep(1)
                    continue
                
                # Extract data dari setiap container
                new_reviews_in_this_batch = 0
                for container in review_containers:
                    if self.max_reviews and len(self.reviews) >= self.max_reviews:
                        break
                    
                    review_data = self.extract_review_data(container, nama_tempat)
                    if review_data:
                        self.reviews.append(review_data)
                        new_reviews_in_this_batch += 1
                        print(f"  [{len(self.reviews)}] {review_data['username'][:30]} - {review_data['rating']} ⭐")
                
                # Update streak counter
                if new_reviews_in_this_batch == 0:
                    no_new_reviews_streak += 1
                    print(f"  ⚠ Tidak ada review baru di batch ini ({no_new_reviews_streak}/{max_no_new_streak})")
                else:
                    no_new_reviews_streak = 0
                
                # Lakukan scroll dengan amount lebih kecil
                scroll_success = self.scroll_review_panel(scroll_element, scroll_amount=1500)
                
                # Sembunyikan gambar setiap 3 scroll
                if scroll_attempts % 3 == 0:
                    self.hide_image_elements()
                    self.hide_gakpenting_elements()
                
                if not scroll_success and scroll_attempts > 10:
                    print("  ⚠ Scroll tidak berhasil memuat konten baru")
                
                scroll_attempts += 1
                
                # Progress report setiap 5 scroll
                if scroll_attempts % 5 == 0:
                    print(f"\n  📊 Progress: {len(self.reviews)} reviews | Scroll: {scroll_attempts}/{max_scroll_attempts}")
                
                # Delay tambahan setiap 10 scroll untuk loading
                if scroll_attempts % 10 == 0:
                    print("  ⏱ Menunggu konten baru dimuat...")
                    time.sleep(3)
            
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
            print(f"\n📊 Statistik:")
            print(f"  • Total reviews: {len(df)}")
            ratings = df[df['rating'] != 'Unknown']['rating'].astype(float)
            if len(ratings) > 0:
                print(f"  • Rating rata-rata: {ratings.mean():.2f}")
            
            print(f"\n📋 Preview data (5 pertama):")
            for i, row in df.head(5).iterrows():
                print(f"\n  {i+1}. {row['username']}")
                print(f"     Rating: {row['rating']} ⭐")
                print(f"     Review: {row['review'][:100]}...")
            
            return True
            
        except Exception as e:
            print(f"✗ Error saat menyimpan: {e}")
            return False


# ===== CARA PENGGUNAAN =====
if __name__ == "__main__":
    # URL Google Maps
    gmaps_url = "https://www.google.com/maps/place/SURYA+KOPITIAM/@-8.2187935,114.367128,16.25z/data=!4m14!1m7!3m6!1s0x2dd1452d6d15a447:0x4171b695db29d8c2!2skopi+jotos!8m2!3d-8.214574!4d114.3706726!16s%2Fg%2F11hwxxn8r_!3m5!1s0x2dd15b1a9ed70e89:0xcf4855f709c8dc35!8m2!3d-8.2205096!4d114.3631858!16s%2Fg%2F11q8rprymb?entry=ttu&g_ep=EgoyMDI1MTAyMC4wIKXMDSoASAFQAw%3D%3D"
    
    # Inisialisasi scraper
    scraper = GoogleMapsReviewScraper(
        url=gmaps_url,
        max_reviews=None  # Ubah ke None untuk ambil semua reviews
    )
    
    # Jalankan scraping
    reviews = scraper.scrape_reviews()
    
    # Simpan hasil
    if reviews:
        scraper.save_to_csv()
    else:
        print("✗ Tidak ada review yang berhasil diambil")