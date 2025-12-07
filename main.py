from databasemanager import MongoDBManager
from new_scraper import IMDbScraper
from dataclasses import dataclass, asdict
import time


@dataclass
class IMDbContent:
    title: str
    rating: float
    year: int
    category: str


MY_URI = "mongodb+srv://oguzbatu2934_db_user:w9vjsbD855H1meI1@cluster0.kejl8qw.mongodb.net/?appName=Cluster0"

MENU_OPTIONS = {
    "1": {"name": "Top 250 Movies", "url": "https://www.imdb.com/chart/top/?ref_=hm_nv_menu"},
    "2": {"name": "Top 250 TV Shows", "url": "https://www.imdb.com/chart/toptv/?ref_=chttp_nv_menu"},
    "3": {"name": "Most Popular Movies", "url": "https://www.imdb.com/chart/moviemeter/?ref_=chttvtp_nv_menu"}
}


def print_menu():
    print("\n" + "=" * 40)
    print("      IMDb SCRAPER FINAL (STABLE)      ")
    print("=" * 40)
    print("1. Top 250 Movies")
    print("2. Top 250 TV Shows")
    print("3. Most Popular Movies")
    print("Q. Exit")
    print("=" * 40)


if __name__ == "__main__":
    db_manager = MongoDBManager(MY_URI, "IMDb_Archive", "Allcontent")
    scraper = IMDbScraper()

    if db_manager.connect():
        while True:
            print_menu()
            choice = input("Secim (1-3 veya Q): ").strip().upper()

            if choice == 'Q':
                break

            if choice in MENU_OPTIONS:
                target = MENU_OPTIONS[choice]

                # Kullanıcıdan sayı iste (Max 25 geleceğini bilse de soruyoruz)
                try:
                    limit = int(input(f"'{target['name']}' kac tane cekilsin? (Max 25): "))
                except:
                    limit = 25

                print(f"\n{target['name']} cekiliyor...")

                data = scraper.scrape_data(target['url'], limit)

                if data:
                    print(f"{len(data)} veri bulundu, kaydediliyor...")
                    count = 0
                    for i, item in enumerate (data,1):
                        content = IMDbContent(
                            title=item["title"],
                            rating=item["rating"],
                            year=item["year"],
                            category=target["name"]
                        )
                        db_manager.insert_data(asdict(content), order_no=i)


                    print(f"Completed. {count} records inserted.")
                else:
                    print("No data inserted.")

                input("\n Press any key to continue...")
            else:
                print("Invalid choice.")
    else:
        print("Database connection failed.")