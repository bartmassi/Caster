This is a system that recommends podcasts based on the contents of articles using natural-language processing. Specifically, articles are transformed using word2vec (https://arxiv.org/abs/1301.3781), and compared to representations of podcasts in the same vector space.

The code in this repository falls into three categories: scraping tools to re-build the podcast database, class definitions/web code (written with Dash) to run the website, and analytical tools to validate the approach used to recommend podcasts.

All code is freely available to be distributed and modified, but credit (either by comment or citation) is appreciated!


====================SCRAPING TOOLS

All scraping tools in this repository are Jupyter notebooks. The scrape starts with iTunes_Scraping.ipynb, which combs iTunes for the titles of every podcast in their library, and then queries the iTunes API in order to get the URL of each podcast's RSS feeds where episodes are hosted. FeedCrawler.ipynb scrapes the RSS feeds of each podcast to get episode descriptions. Finally, FeedCleaner.ipynb processes the episode descriptions and generates a word2vec representation of each podcast. 


====================WEBSITE TOOLS

In order to run the website, two files are necessary: a database containing the podcast metadata and word2vec representations, and a trained word2vec model. One possible source is google's pre-trained model (https://code.google.com/archive/p/word2vec/). 

The main file for the site is caster_site.py. This will run the code for displaying the website and handling user input. There are two important classes for getting this site to run: PodcastDB.py, and Cleaner.py. The former is a class for interfacing with the podcast database, and the latter is a class that preprocesses text. 


====================ANALYTICAL TOOLS

The sole file for analytics is Validate_Model.ipynb. This file contains a number of analyses aimed at demonstrating that the word2vec representations of podcasts are a valid way of representing what a podcast is about, and that the system makes sensible recommendations.
