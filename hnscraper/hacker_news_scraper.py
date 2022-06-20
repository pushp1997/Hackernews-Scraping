"""
Hackernews Scraper
Author: Pushp Vashisht
License: MIT
"""

import json
from logging import Logger, getLogger
from pathlib import Path
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


class HackerNewsScraper:
    """Scraper class"""

    HOME_PAGE_URL = "https://thehackernews.com/"

    def __init__(self, pages_to_scrape: int = 5) -> None:
        self.pages_to_scrape = pages_to_scrape
        self.page_soups: List[BeautifulSoup] = []
        self.posts_url_title_data: List[Dict[str, str]] = []
        self.posts_url_others_data: List[Dict[str, str]] = []

    @staticmethod
    def link_to_soup(link: str) -> BeautifulSoup:
        """This method returns the soup of a link"""
        logger: Logger = getLogger(__name__)
        try:
            response = requests.get(link, timeout=1)
            if response.ok:
                return BeautifulSoup(response.text, "html.parser")
            return BeautifulSoup()
        except requests.exceptions.Timeout:
            logger.info("Request timed out for %s, skipping this page..", link, exc_info=True)
            return BeautifulSoup()
        except requests.exceptions.ConnectionError as err:
            logger.info(
                "Error occured while connecting to the page for %s, skipping this page..",
                link,
                exc_info=True,
            )
            logger.error(err)
            return BeautifulSoup()
        except requests.exceptions.RequestException as err:
            logger.info(
                "Some error occured while requesting the page for %s, skipping this page..",
                link,
                exc_info=True,
            )
            logger.error(err)
            return BeautifulSoup()

    def scrape(self) -> None:
        """This methos scrapes the pages and creates soup for all pages"""
        if self.pages_to_scrape < 1:
            return

        home_page_soup = HackerNewsScraper.link_to_soup(HackerNewsScraper.HOME_PAGE_URL)
        self.page_soups.append(home_page_soup)

        for i in range(self.pages_to_scrape - 1):
            next_page_link = self.page_soups[i].find("a", class_="blog-pager-older-link-mobile")[
                "href"
            ]
            self.page_soups.append(HackerNewsScraper.link_to_soup(next_page_link))

    def extract(self) -> None:
        """This methos extracts posts data from the soups of all pages"""
        if self.pages_to_scrape < 1:
            return

        for page in self.page_soups:
            posts_in_page = page.find_all("a", class_="story-link")
            for post in posts_in_page:
                self.posts_url_title_data.append(
                    {"url": post["href"], "title": post.find("h2", class_="home-title").text}
                )

                self.posts_url_others_data.append(
                    {
                        "url": post["href"],
                        "desc": post.find("div", class_="home-desc").text,
                        "author": post.find("span").text[1 : len(post.find("span").text) - 1],
                        "imgSrc": post.find("img")["data-src"],
                    }
                )

    def save_to_mongo(self):
        """This method saves the extracted data to MongoDB"""
        mongodb_uri = input("Enter the mongoDbURI: ")
        # for users running mongo server on local machine: 'mongodb://localhost:27017/'
        client = MongoClient(mongodb_uri)  # type: ignore
        # Getting the database client
        database = client["hackernews"]

        # Getting the collections
        url_title = database["url-title"]
        url_others = database["url-others"]
        url_title.insert_many(self.posts_url_title_data)
        url_others.insert_many(self.posts_url_others_data)

    def save_to_json(self):
        """This method saves the extracted data to a JSON file"""
        # Merge data into a single dictionary
        no_of_posts = len(self.posts_url_title_data)
        posts_url_data = [
            dict(self.posts_url_title_data[0], **self.posts_url_others_data[0])
            for i in range(no_of_posts)
        ]
        output_location = input("Enter the location to save the JSON to: ")
        output_path = Path(output_location)

        # Create any necessary parent directories
        if not output_path.parent.exists():
            print(f"Directory {output_path.parent} does not exist, creating.")
            output_path.parent.mkdir(parents=True)

        # Save JSON
        with open(output_path, "w", encoding="UTF8") as output_file:
            print(f"Saving to {output_path}.")
            output_file.write(json.dumps(posts_url_data))
