from databasemanager import MongoDBManager
from new_scraper import IMDbScraper
from dataclasses import dataclass, asdict


@dataclass
class IMDbContent:
    title: str
    rating: float
    year: int
    category: str
    watched: bool = False


MY_URI = "mongodb+srv://oguzbatu2934_db_user:MYPASSWORD@cluster0.kejl8qw.mongodb.net/?appName=Cluster0"

MENU_OPTIONS = {
    "1": {"name": "Top 250 Movies", "url": "https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc"},
    "2": {"name": "Top 250 TV Shows","url": "https://www.imdb.com/chart/toptv/?ref_=sr_nv_menu"},
    "3": {"name": "Most Popular Movies (100) ", "url": "https://www.imdb.com/chart/moviemeter/?ref_=chttp_nv_menu"}
}


def print_menu():
    print("\n" + "=" * 40)
    print("      IMDB SCRAPER w/SELENIUM      ")
    print("=" * 40)
    print("1. Top 250 Movies")
    print("2. Top 250 TV Shows")
    print("3. Most Popular Movies")
    print("---ALGORITHM---")
    print("4. Find highest Rating ")
    print("5. Mark a Movie as Watched")
    print("6. Show My Watched Movies")
    print("7. Remove from Watched List")
    print("Q. Exit")
    print("=" * 40)


def filter_by_rating(db_manager: MongoDBManager):
    try:
        min_rating = float(input("Minimum Rating: (e.g. 8.3):"))
        query = {"rating": {"$gte": min_rating}}
        results = list(db_manager.collection.find(query).sort("rating", -1))
        if results:
            print(f"\n Found {len(results)} movies with minimum rating {min_rating} +:")
            for i, item in enumerate(results, 1):
                status = "Watched" if item.get("watched") else " "
                print(f"{i}.{item['title']}  | {item['rating']} {status}")
        else:
            print("No Movies found above rating")
    except ValueError:
        print(" Invalid Number or range entered.")


def select_movie_from_search(db_manager, action_text):
    search_name = input(f" Enter movie name to search: {action_text}: ").strip()
    matches = list(db_manager.collection.find({"title": {"$regex": search_name, "$options": "i"}}).limit(10))
    if not matches:
        print(" No matches found.")
        return None
    if len(matches) == 1:
        movie = matches[0]
        confirm = input(f" did you mean {movie['title']} ({movie['year']}) ? (Y/N):").upper()
        if confirm == "Y":
            return movie
        else:
            return None
    print(f" Found {len(matches)} movies with {action_text}  Please select one:")
    for i, m in enumerate(matches, 1):
        status = "Watched" if m.get("watched") else " "
        print(f"{i}.{m['title']}   {m['year']} {status}")
    try:
        selection = int(input(" Select number (0 to cancel): "))
        if 1 <= selection <= len(matches):
            return matches[selection - 1]
        else:
            return None
    except ValueError:
        return None


def mark_as_watched(db_manager):
    movie = select_movie_from_search(db_manager, "to convert it to watched")
    if movie:
        db_manager.collection.update_one({"_id": movie["_id"]}, {"$set": {"watched": True}})
        print(f" Succes! {movie['title']} has been marked as watched! .")


def show_watched_list(db_manager: MongoDBManager):
    query = {"watched": True}
    results = list(db_manager.collection.find(query))
    if results:
        print(f"\n Your watched list length is : --> {len(results)} :")
        print("-" * 40)
        for i, item in enumerate(results, 1):
            print(f"{i}. {item['title']} | {item['rating']} ")
        print("-" * 40)
    else:
        print("You haven't marked any movies or series as watched yet.")


def remove_from_watched_list(db_manager):
    movie = select_movie_from_search(db_manager, "remove from watched")
    if movie:
        if movie.get("watched") == True:
            db_manager.collection.update_one({"_id": movie["_id"]}, {"$set": {"watched": False}})
            print(f" Success! '{movie['title']}' removed from your watched list.")
        else:
            print(f" '{movie['title']}' was not in your watched list anyway.")


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="IMDb Scraper with Selenium")
    parser.add_argument("--headless", action="store_true", help="Run browser in background")
    args = parser.parse_args()

    db_manager = MongoDBManager(MY_URI, "IMDb_Archive", "Allcontent")

    try:
        if db_manager.connect():
            while True:
                print_menu()
                choice = input("Choice: ").strip().upper()

                if choice == 'Q':
                    print(" Exiting Program...")
                    break

                if choice in MENU_OPTIONS:
                    target = MENU_OPTIONS[choice]
                    try:
                        limit = int(input(f"Count for '{target['name']}'  (Max 250+): "))
                    except:
                        limit = 25

                    print(f"\n  Starting Selenium Scraper for {target['name']} ...")

                    scraper = IMDbScraper(headless=args.headless)

                    try:
                        data = scraper.scrape_data(target['url'], limit)

                        if data:
                            print(f"{len(data)} items found, saving to MongoDB...")
                            for i, item in enumerate(data, 1):
                                content = IMDbContent(
                                    title=item["title"],
                                    rating=item["rating"],
                                    year=item["year"],
                                    category=target["name"]
                                )
                                db_manager.insert_data(asdict(content), order_no=i)
                            print("Completed.")
                        else:
                            print("No data inserted.")

                    except Exception as e:
                        print(f"Error during scraping process: {e}")

                    finally:
                        scraper.close()
                        print("Browser closed.")

                    input("\n Press Enter to continue...")


                elif choice == '4':
                    filter_by_rating(db_manager)
                    input("\n Press Enter to continue...")

                elif choice == '5':
                    mark_as_watched(db_manager)
                    input("\n Press Enter to continue...")

                elif choice == '6':
                    show_watched_list(db_manager)
                    input("\n Press Enter to continue...")

                elif choice == '7':
                    remove_from_watched_list(db_manager)
                    input("\n Press Enter to continue...")

                else:
                    print("Invalid choice.")

    except KeyboardInterrupt:
        print("\nExiting program...")