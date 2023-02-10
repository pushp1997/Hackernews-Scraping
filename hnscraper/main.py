"""
Hackernews Scraper
Author: Pushp Vashisht
License: MIT
"""

from hnscraper.hacker_news_scraper import HackerNewsScraper


def main():
    """Main Function"""
    no_pages = int(input("How many pages to extract the data from? "))
    scraper = HackerNewsScraper(no_pages)
    scraper.scrape()
    scraper.extract()
    print("Choose DB to save data: \n 1. MongoDB \n 2. MySQL")
    db_choice = int(input("Choose option 1 or 2\n"))
    if db_choice == 1:
        scraper.save_to_mongo();
    else:
        scraper.save_to_sqldb()
    scraper.save_to_json()


if __name__ == "__main__":
    main()
