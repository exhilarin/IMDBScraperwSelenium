from databasemanager import MongoDBManager
from new_scraper import IMDbScraper
from dataclasses import dataclass , asdict
import time

@dataclass
class IMDbContent:
    title: str
    rating: float
    year: int
    category: str


MY_URI = "mongodb+srv://oguzbatu2934_db_user:MYPASSWORD@cluster0.kejl8qw.mongodb.net/?appName=Cluster0"

Target_Urls = {
    "Top 250 TV Shows": "https://www.imdb.com/chart/toptv/?ref_=chttp_nv_menu",
    "Top 250 Movies": "https://www.imdb.com/chart/top/?ref_=hm_nv_menu",
    "Most Popular Movies":"https://www.imdb.com/chart/moviemeter/?ref_=chttvtp_nv_menu"
}

if __name__ == "__main__":
    print("---- ULTIMATE IMDB ARCHIVE STARTING ----\n")

    db_manager = MongoDBManager(MY_URI, "IMDb_Archive","Allcontent")
    scraper = IMDbScraper()

    if db_manager.connect():
        for category_name , url_address in Target_Urls.items():
            print(f" Processing Target: {category_name}")
            print(f"URL: {url_address}")

            scrapped_data= scraper.scrape_data(url_address)
            if scrapped_data:
                print(f" {len(scrapped_data)} items scraped saving to database...")
                count =0
                for item in scrapped_data:
                    content_object = IMDbContent(
                        title=item["title"],
                        rating=item["rating"],
                        year=item["year"],
                        category=category_name
                    )
                    db_manager.insert_data(asdict(content_object))
                    count+=1
                print(f"{category_name}completed! ({count}records saved) ")
            else:
                print(f" No Data returned for {category_name}")
            print("Cooldown ( 2 seconds)...")
            time.sleep(2)
        print(" ALL LISTS ARCHIEVED SUCCESSFULLY")
    else:
        print("Critical Error : Database Connection Failed. Check your connection or password.")

# main.py dosyasının EN ALTINA bunu ekle ve çalıştır:

print("\n--- 🕵️‍♂️ DOĞRULAMA ZAMANI: İSİMLERİ OKUYORUM ---")

records=db_manager.collection.find()

for record in records:
    title=record.get("title" ,"Unknown Title")
    category=record.get("category","Unknown Category")
    rating=record.get("rating",0.0)
    year=record.get("year",0)

    print(f" {title} ({rating}) ({year}) [{category}]")

