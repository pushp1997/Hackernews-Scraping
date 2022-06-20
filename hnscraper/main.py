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
    scraper.save_to_mongo()
    scraper.save_to_json()


if __name__ == "__main__":
    main()
