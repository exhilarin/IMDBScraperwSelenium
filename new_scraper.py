import requests
from bs4 import BeautifulSoup


class IMDbScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

    def scrape_data(self, chart_url, limit=10):
        print(f"Connecting to IMDb: {chart_url}")

        try:
            response = requests.get(chart_url, headers=self.headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                metadata_list = soup.find("ul", {"class": "ipc-metadata-list"})

                if not metadata_list:
                    print("Error: List container not found.")
                    return []

                items_html = metadata_list.find_all("li")
                extracted_data = []

                # Limit kontrolü burada
                for item in items_html[:limit]:
                    try:
                        # TITLE
                        title_tag = item.find("h3", {"class": "ipc-title__text"})
                        if title_tag:
                            if ". " in title_tag.text:
                                title = title_tag.text.split(". ", 1)[1]
                            else:
                                title = title_tag.text
                        else:
                            title = "Unknown"

                        # RATING (Senin istedigin ozel sinif)
                        rating = 0.0
                        rating_tag = item.find("span", {"class": "ipc-rating-star--rating"})

                        if rating_tag:
                            try:
                                rating = float(rating_tag.text)
                            except ValueError:
                                rating = 0.0
                        else:
                            # Yedek (Base)
                            base_tag = item.find("span", {"class": "ipc-rating-star--base"})
                            if base_tag:
                                try:
                                    rating = float(base_tag.text.split()[0])
                                except:
                                    rating = 0.0

                        # YEAR
                        metadata_items = item.find_all("span", {"class": "cli-title-metadata-item"})
                        year = 0
                        if metadata_items:
                            year_text = metadata_items[0].text
                            if year_text.isdigit():
                                year = int(year_text)

                        data = {
                            "title": title,
                            "rating": rating,
                            "year": year,
                        }
                        extracted_data.append(data)

                    except Exception:
                        continue

                print(f"Successfully fetched {len(extracted_data)} items.")
                return extracted_data
            else:
                print(f"Connection Failed. Status Code: {response.status_code}")
                return []

        except Exception as e:
            print(f"Unexpected Error: {e}")
            return []