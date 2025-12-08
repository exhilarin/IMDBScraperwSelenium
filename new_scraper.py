from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


class IMDbScraper:
    def __init__(self, headless=False):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")

        chrome_options.add_argument("--lang=en-US")
        prefs = {
            "intl.accept_languages": "en-US,en",
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")  # Tam ekran gibi aç
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        print(" Initializing Selenium WebDriver...")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def scrape_data(self, chart_url, limit=50):
        print(f" Connecting to IMDb via Selenium: {chart_url}")
        self.driver.get(chart_url)

        extracted_data = []

        try:
            print(" Waiting for page to load...")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ipc-metadata-list-summary-item"))
            )

            while len(extracted_data) < limit:

                items = self.driver.find_elements(By.CLASS_NAME, "ipc-metadata-list-summary-item")


                current_batch = []

                for item in items:
                    if len(current_batch) >= limit:
                        break

                    try:
                        # TITLE
                        try:
                            title_el = item.find_element(By.CLASS_NAME, "ipc-title__text")
                            raw_title = title_el.text.strip()
                            if ". " in raw_title:
                                title = raw_title.split(". ", 1)[1]
                            else:
                                title = raw_title
                        except:
                            title = "Unknown"

                        # RATING
                        try:
                            rating_el = item.find_element(By.CLASS_NAME, "ipc-rating-star--rating")
                            rating = float(rating_el.text)
                        except:
                            rating = 0.0

                        # YEAR
                        try:

                            metas = item.find_elements(By.CLASS_NAME, "dli-title-metadata-item")
                            if not metas:
                                metas = item.find_elements(By.CLASS_NAME, "cli-title-metadata-item")

                            year = 0
                            for m in metas:
                                txt = m.text.strip()
                                if txt.isdigit() and len(txt) == 4:
                                    year = int(txt)
                                    break
                        except:
                            year = 0

                        data = {"title": title, "rating": rating, "year": year}
                        current_batch.append(data)

                    except:
                        continue


                extracted_data = current_batch

                if len(extracted_data) >= limit:
                    print(f"🎯 Target reached: {len(extracted_data)} items.")
                    break

                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)

                    load_more_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "ipc-see-more__button"))
                    )

                    self.driver.execute_script("arguments[0].click();", load_more_btn)

                    print(f" Loading more items... (Current: {len(extracted_data)})")
                    time.sleep(3)

                except Exception:
                    print(f" End of list or 'Load More' button not found. Stopping with {len(extracted_data)} items.")
                    break

            print(f" Successfully fetched {len(extracted_data)} items.")
            return extracted_data

        except Exception as e:
            print(f" Scraper Error: {e}")
            return extracted_data

    def close(self):
        try:
            self.driver.quit()
        except:
            pass