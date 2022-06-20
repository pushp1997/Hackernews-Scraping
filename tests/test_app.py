import pytest
from hnscraper.app import HackerNewsScraper


def test_class_initialization():
    """This test checks if the class is initialized properly"""
    no_pages = 0
    scraper = HackerNewsScraper(no_pages)
    assert scraper.pages_to_scrape is no_pages
    assert len(scraper.page_soups) == 0
    assert len(scraper.posts_url_title_data) == 0
    assert len(scraper.posts_url_others_data) == 0


@pytest.mark.parametrize(
    "no_pages,expected",
    [
        (0, 0),
        (1, 1),
        (2, 2),
    ],
)
def test_scraping_and_extraction_with_multi_pages(no_pages, expected):
    """This test checks if the scraper works with multiple pages"""
    scraper = HackerNewsScraper(no_pages)
    assert scraper.pages_to_scrape == expected
    scraper.scrape()
    assert len(scraper.page_soups) == expected
    scraper.extract()
    assert len(scraper.posts_url_title_data) == len(scraper.posts_url_others_data)
