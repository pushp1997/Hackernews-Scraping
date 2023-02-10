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
import pymysql


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
                        "author": post.find("span").text[1: len(post.find("span").text) - 1],
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

    def save_to_sqldb(self):
        def mysqlconnect():
            # To connect MySQL database
            conn = pymysql.connect(
                host='localhost',
                user='root',
                password="Password1!",
                db='scraper',
            )
            return conn

        conn_obj = mysqlconnect()
        conn_cursor = conn_obj.cursor()

        # DB creation
        sql_db_create = "create database if not exists scraper;"

        # Use DB created
        sql_use_db = "use scraper;"

        # create table "urlTitle" to store [urlLink, urlTitle]
        sql_create_urlTitle_table = "create table if not exists urltitle(\
          url_title_id int auto_increment primary key,\
          url_link text not null,\
          url_title text not null)"

        # create table "urlotherInfo" to store [urlLink, urlTitle, urlAuthor, urlImgSrc]
        sql_create_urlOtherInfo_table = "create table if not exists urlotherinfo(\
          id int auto_increment primary key,\
          url_link text not null,\
          url_description text not null,\
          author text not null,\
          imgsrc text not null)"

        conn_cursor.execute(sql_db_create)
        conn_cursor.execute(sql_use_db)
        conn_cursor.execute(sql_create_urlTitle_table)
        conn_cursor.execute(sql_create_urlOtherInfo_table)

        sql_insert_urlTitle = "insert into urltitle(url_link, url_title) values (%s, %s)"
        sql_insert_urlOtherInfo = "insert into urlotherinfo(url_link, url_description, author, imgSrc) values (%s, %s, %s, %s)"
        for url_title, url_other in zip(self.posts_url_title_data, self.posts_url_others_data):
            conn_cursor.execute(sql_insert_urlTitle, (url_title["url"], url_title["title"]))
            conn_cursor.execute(sql_insert_urlOtherInfo,
                                (url_other["url"], url_other["desc"], url_other["author"], url_other["imgSrc"]))
