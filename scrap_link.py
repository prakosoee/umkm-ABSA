from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import time
import re
import pandas as pd
from datetime import datetime
import os


class GoogleMapsSearchScraper:
    def __init__(self, query, max_places=50, scroll_pause=1.2, headless=False):
        self.query = query
        self.max_places = max_places
        self.scroll_pause = scroll_pause
        self.headless = headless
        self.driver = None
        self.results = []
        self.seen_links = set()

    def setup_driver(self):
        options = Options()
        options.add_argument("--lang=id")
        options.add_argument("--accept-language=id-ID,id")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        if self.headless:
            options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        try:
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception:
            pass

    def open_and_search(self):
        print("⟳ Membuka Google Maps dan melakukan pencarian...")
        self.driver.get("https://www.google.com/maps")
        wait = WebDriverWait(self.driver, 20)
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.searchboxinput"))
        )
        search_input.clear()
        search_input.send_keys(self.query)
        search_input.send_keys(Keys.ENTER)
        print(f"✓ Pencarian dikirim: '{self.query}'")
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb")))
        except TimeoutException:
            pass
        time.sleep(2)
        print("✓ Halaman hasil pencarian dimuat (awal)")

    def get_results_container(self):
        selectors = [
            "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd",  # target utama sesuai permintaan
            "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde",
            "div.m6QErb.DxyBCb.kA9KIf.dS8AEf",
            "div.m6QErb.DxyBCb"
        ]
        for sel in selectors:
            try:
                el = self.driver.find_element(By.CSS_SELECTOR, sel)
                if el:
                    print(f"✓ Menemukan container hasil: {sel}")
                    return el
            except Exception:
                continue
        return None

    def scroll_results(self, container, target_count=None, max_attempts=300, max_stagnant=8):
        last_height = -1
        prev_unique = 0
        attempts = 0
        stagnant = 0
        print(f"⟳ Mulai infinite scroll hingga {target_count if target_count else 'semua'} tempat terlihat...")
        while True:
            try:
                # Hitung anchor unik berdasarkan href, HANYA di dalam container
                anchors = container.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
                hrefs = {a.get_attribute("href") for a in anchors if a.get_attribute("href")}
                current_unique = len(hrefs)

                # Cek target terpenuhi
                if target_count and current_unique >= target_count:
                    print(f"✓ Target tercapai: {current_unique}/{target_count} anchor")
                    break

                # Cek stagnasi
                if current_unique > prev_unique:
                    prev_unique = current_unique
                    stagnant = 0
                else:
                    stagnant += 1
                if stagnant >= max_stagnant:
                    print(f"⚠ Stagnan {stagnant} kali. Total anchor terlihat: {current_unique}")
                    break

                # Cek batas percobaan
                if attempts >= max_attempts:
                    print(f"⚠ Mencapai batas percobaan scroll: {max_attempts}")
                    break

                # Scroll
                current = self.driver.execute_script("return arguments[0].scrollTop", container)
                height = self.driver.execute_script("return arguments[0].scrollHeight", container)
                self.driver.execute_script("arguments[0].scrollBy(0, 1200)", container)
                time.sleep(self.scroll_pause)
                new_current = self.driver.execute_script("return arguments[0].scrollTop", container)
                if new_current == current and height == last_height:
                    # fallback: PAGE_DOWN
                    try:
                        container.send_keys(Keys.PAGE_DOWN)
                    except Exception:
                        pass
                    time.sleep(self.scroll_pause)
                last_height = height
                attempts += 1
                if attempts % 10 == 0:
                    print(f"  📊 Progress scroll: anchors={current_unique} | attempts={attempts}")
            except Exception:
                time.sleep(self.scroll_pause)

    def parse_lat_lng(self, url):
        m = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
        if m:
            return m.group(1), m.group(2)
        m2 = re.search(r"/@(-?\d+\.\d+),(-?\d+\.\d+)", url)
        if m2:
            return m2.group(1), m2.group(2)
        return None, None

    def collect_list_items(self, container):
        anchors = container.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
        items = []
        for a in anchors:
            try:
                name = a.get_attribute("aria-label") or ""
                href = a.get_attribute("href") or ""
                if not href or href in self.seen_links:
                    continue
                lat, lng = self.parse_lat_lng(href)
                items.append({
                    "name": name,
                    "link": href,
                    "latitude": lat,
                    "longitude": lng,
                    "element": a
                })
            except Exception:
                continue
        print(f"✓ Mengumpulkan anchors dari container: {len(items)} ditemukan")
        return items

    def get_text_safe(self, by, selector, timeout=5):
        try:
            el = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, selector)))
            return el.text.strip()
        except Exception:
            return ""

    def get_detail_field(self, xpath_variants, timeout=6):
        for xp in xpath_variants:
            try:
                el = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xp)))
                txt = el.text.strip()
                if txt:
                    return txt
            except Exception:
                continue
        return ""

    def open_item_and_extract_details(self, item):
        try:
            print(f"⟳ Membuka detail: {item.get('name','')}...")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item["element"])
            time.sleep(0.2)
            self.driver.execute_script("arguments[0].click();", item["element"])
        except Exception:
            try:
                item["element"].click()
            except Exception:
                return None
        wait = WebDriverWait(self.driver, 15)
        try:
            # Tunggu judul terlihat (lebih ketat dari sekadar presence)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob")))
        except TimeoutException:
            time.sleep(1)

        # Scope semua pencarian field ke panel detail yang memiliki h1
        detail_root = None
        try:
            detail_root = self.driver.find_element(
                By.XPATH,
                "//div[contains(@class,'m6QErb') and .//h1[contains(@class,'DUwDvf')]]"
            )
        except Exception:
            detail_root = None

        # Ambil name dari panel detail
        name_detail = item.get("name", "")
        try:
            if detail_root:
                name_detail = detail_root.find_element(By.CSS_SELECTOR, "h1.DUwDvf.lfPIob").text.strip() or name_detail
            else:
                name_detail = self.get_text_safe(By.CSS_SELECTOR, "h1.DUwDvf.lfPIob", timeout=4) or name_detail
        except Exception:
            pass

        # Ambil category dari panel detail
        category = ""
        try:
            if detail_root:
                category = detail_root.find_element(By.CSS_SELECTOR, "button.DkEaL").text.strip()
            else:
                category = self.get_detail_field(["//button[contains(@class,'DkEaL')]"] , timeout=4)
        except Exception:
            category = ""

        # Ambil address dari panel detail (beberapa selector)
        address = ""
        if detail_root:
            for sel in [
                "button[data-item-id='address'] div.Io6YTe",
                "[data-item-id='address'] div.Io6YTe",
            ]:
                try:
                    address_el = detail_root.find_element(By.CSS_SELECTOR, sel)
                    txt = address_el.text.strip()
                    if txt:
                        address = txt
                        break
                except Exception:
                    continue
            if not address:
                try:
                    address = detail_root.find_element(
                        By.XPATH,
                        ".//button[contains(@aria-label,'Alamat')]/div[contains(@class,'Io6YTe')]"
                    ).text.strip()
                except Exception:
                    address = ""
        else:
            address = self.get_detail_field([
                "//button[contains(@aria-label,'Alamat')]/div[contains(@class,'Io6YTe')]",
                "//button[contains(@data-item-id,'address')]/div[contains(@class,'Io6YTe')]",
                "//div[contains(@class,'Io6YTe') and ancestor::button[contains(@aria-label,'Alamat')]]",
            ], timeout=4)

        # Ambil phone dari panel detail
        phone = ""
        if detail_root:
            phone_xpaths = [
                ".//button[contains(@aria-label,'Telepon')]/div[contains(@class,'Io6YTe')]",
                ".//button[contains(@aria-label,'Nomor')]/div[contains(@class,'Io6YTe')]",
                ".//button[contains(@data-item-id,'phone')]/div[contains(@class,'Io6YTe')]",
                ".//a[starts-with(@href,'tel:')]/div[contains(@class,'Io6YTe')]",
            ]
            for xp in phone_xpaths:
                try:
                    txt = detail_root.find_element(By.XPATH, xp).text.strip()
                    if txt:
                        phone = txt
                        break
                except Exception:
                    continue
            # Tambahkan fallback berbasis CSS class yang Anda sebutkan
            if not phone:
                phone_css_selectors = [
                    "button[data-item-id='phone'] div.Io6YTe.fontBodyMedium.kR99db.fdkmkc",
                    "a[href^='tel:'] div.Io6YTe.fontBodyMedium.kR99db.fdkmkc",
                    "button[aria-label*='Telepon'] div.Io6YTe.fontBodyMedium.kR99db.fdkmkc",
                    "div.Io6YTe.fontBodyMedium.kR99db.fdkmkc",
                ]
                for sel in phone_css_selectors:
                    try:
                        el = detail_root.find_element(By.CSS_SELECTOR, sel)
                        txt = el.text.strip()
                        if txt:
                            phone = txt
                            break
                    except Exception:
                        continue
        else:
            phone = self.get_detail_field([
                "//button[contains(@aria-label,'Telepon')]/div[contains(@class,'Io6YTe')]",
                "//button[contains(@aria-label,'Nomor')]/div[contains(@class,'Io6YTe')]",
                "//button[contains(@data-item-id,'phone')]/div[contains(@class,'Io6YTe')]",
                "//a[starts-with(@href,'tel:')]/div[contains(@class,'Io6YTe')]",
            ], timeout=4)

        data = {
            "name": name_detail or item.get("name", ""),
            "link": item.get("link", ""),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
            "address": address,
            "phone": phone,
            "category": category,
        }
        print(f"✓ Extracted: name='{data['name'][:40]}', category='{data['category'][:30]}', phone='{data['phone'][:20]}'")
        return data

    def scrape(self):
        try:
            self.setup_driver()
            self.open_and_search()
            container = None
            for _ in range(20):
                container = self.get_results_container()
                if container is not None:
                    break
                time.sleep(0.5)
            if container is None:
                return []
            # Infinite scroll until enough places are visible
            print(f"⟳ Mulai memuat daftar tempat hingga {self.max_places}...")
            self.scroll_results(container, target_count=self.max_places)
            all_items = self.collect_list_items(container)
            # Batasi ke max_places
            if self.max_places:
                all_items = all_items[: self.max_places]
            print(f"⟳ Mulai klik dan ekstraksi detail dari {len(all_items)} tempat...")
            for idx, item in enumerate(all_items, start=1):
                if self.max_places and len(self.results) >= self.max_places:
                    break
                if item["link"] in self.seen_links:
                    continue
                details = self.open_item_and_extract_details(item)
                if details:
                    self.results.append(details)
                    self.seen_links.add(item["link"]) 
                    if idx % 5 == 0:
                        print(f"  📊 Progress detail: {len(self.results)} / {len(all_items)} selesai")
            print(f"✓ Selesai ekstraksi. Total hasil: {len(self.results)}")
            return self.results
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass

    def save_to_csv(self, filename=None):
        if not self.results:
            return None
        os.makedirs("dataset", exist_ok=True)
        if not filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_q = re.sub(r"\W+", "_", self.query).strip("_")[:50]
            filename = f"dataset/places_{safe_q}_{ts}.csv"
        df = pd.DataFrame(self.results)
        # De-duplicate hasil berdasarkan link (stabil)
        if "link" in df.columns:
            df = df.drop_duplicates(subset=["link"]).reset_index(drop=True)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        return filename


if __name__ == "__main__":
    q = "geprek kak rose"
    scraper = GoogleMapsSearchScraper(query=q, max_places=50, headless=False)
    data = scraper.scrape()
    if data:
        out = scraper.save_to_csv()
        print(f"saved: {out} | rows: {len(data)}")
    else:
        print("no data scraped")
