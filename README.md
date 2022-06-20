# Hackernews-Scraping
![Tests](https://github.com/pushp1997/Hackernews-Scraping/actions/workflows/tests.yml/badge.svg)
### Business Requirements:

1. Scrape TheHackernews.com and store the result (Description, Image, Title, Url) in mongo db
2. Maintain two relations - 1 with the url and title of the blog and other one with url and its meta data like (Description, Image, Title, Author)

### Requirements:

-   python3
-   pip
-   python libraries:
    _ requests
    _ BeautifulSoup4
    _ pymongo
    _ jupyterlab \* notebook
-   MongoDB
-   git

## To run the application on your local machine:

### Clone the repository:

1. Type the following in your terminal

    `git clone https://github.com/pushp1997/Hackernews-Scraping.git`

2. Change the directory into the repository

    `cd ./Hackernews-Scraping`

3. Create python virtual environment

    `python3 -m venv ./scrapeVenv`

4. Activate the virtual environment created

    - On linux / MacOS :
      `source ./scrapeVenv/bin/activate`
    - On Windows (cmd) :
      `"./scrapeVenv/Scripts/activate.bat"`
    - On Windows (powershell) :
      `"./scrapeVenv/Scripts/activate.ps1"`

5. Install python requirements

    `pip install -r requirements.txt`

6. Open the ipynb using jupyter notebook

    `jupyter notebook "Hackernews Scraper.ipynb"`

7. Run the notebook, you will be asked to provide inputs for no of pages to scrape to get the post and your MongoDB database URI to store the posts data.

8. Open mongodb shell connecting to the same URI you provided to the ipynb notebook while running it.

9. Change the database

    `use hackernews`

10. Print the documents in the 'url-title' collection

    `db["url-title"].find().pretty()`

11. Print the documents in the 'url-others' collection

    `db["url-others"].find().pretty()`
