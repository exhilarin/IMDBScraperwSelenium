import requests
from bs4 import BeautifulSoup
from urllib3.util import url


class IMDbScraper:
    def __init__(self):
        # Artık sabit bir URL yok, tarayıcı kimliğimiz sabit.
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9" }
    def scrape_data(self,url):

        print(f"Connecting to IMDB: {url} ...")
        try:
            response = requests.get(url,headers=self.headers)
            if response.status_code ==200:
                soup =BeautifulSoup(response.content,"html.parser")
                metadata_list =soup.find("ul",class_="ipc-metadata-list")

                if not metadata_list:
                    print("Error: Could not find the list container . HTML structure might have changed")
                    return []
                items_html = metadata_list.find_all("li")
                extracted_data =[]
                for item in items_html:
                    try:
                        #---------TITLE---------
                        title_tag=item.find("h3",{"class":"ipc-title__text"}).text
                        if title_tag:
                            title_next=title_tag.next
                            if". " in title_next:
                                title=title_next.split(". ",1)[1]
                            else:
                                title=title_next
                        else:
                            title="Unknown Title"

                    #---------RATING-----------

                        rating_star=item.find("span ",{"class":"ipc-rating-star--rating"}).text
                        rating=float(rating_star.text) if rating_star else 0.0

                    #YEAR
                        metadata_items=item.find_all("span",class_="cli-title-metadata-item ")
                        year=0
                        if metadata_items:
                            year_text=metadata_items[0].text
                            if year_text.isdigit():
                                year=int(year_text)

                        data ={
                            "title":title,
                            "rating":rating,
                            "year":year,
                        }
                        extracted_data.append(data)
                    except Exception:
                        continue  # Hatalı satırı atla, döngüye devam et

        # Döngü tamamen bittiğinde burası çalışır
                print(f"✅ Successfully fetched {len(extracted_data)} items.")
                return extracted_data

            else:
    # Burası "if response.status_code == 200" bloğunun ELSE kısmıdır
    # Yani bağlantı var ama sayfa bulunamadı (404, 500 vb.)
    # DİKKAT: Burada 'e' değişkeni yoktur, status_code yazdırılır.
                print(f"❌ Connection Failed. Status Code: {response.status_code}")
                return []

        except Exception as e:
    # Burası EN BAŞTAKİ "try" bloğunun eşidir.
    # İnternet kesilmesi gibi genel hataları yakalar. 'e' burada tanımlıdır.
            print(f"❌ Unexpected Error: {e}")
            return []