import requests
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin, urlparse

# html tags that do not contain valueable text
not_parse = ['button', 'style', 'script', 'svg', 'form', 'nav', 'header', 'footer', 'menu']
not_parse_class = ['.menu', '.banner']

def clean_soup(soup):

    # remove comments:
    for comments in soup.find_all(text=lambda text:isinstance(text, Comment)):
        comments.extract()

    # remove unnecessary tags from soup
    for tag in not_parse:
        for el in soup.find_all(tag):
            el.extract()

    for cl in not_parse_class:
        for el in soup.select(cl):
            el.extract()

    # remove head
    soup.find('head').extract()

    return soup