import pandas as pd
import re
import ratelim

import requests
from bs4 import BeautifulSoup as bs


@ratelim.patient(3, 1)
def parse_article(path):
    try:
        response = requests.get("https://cyberleninka.ru" + path)
        response.raise_for_status()

        soup = bs(response.text, "html.parser")

        article = " ".join([p.get_text() for p in soup.find("div", {"class": "ocr"}).find_all("p")])
        article = re.split("литература", article, flags=re.IGNORECASE)[0]
        article = re.sub(u"\ufeff", "", article)
        article = re.sub("\n", " ", article)
        article = re.sub("\r", " ", article)
        article = re.sub("\t", " ", article)

    except requests.exceptions.HTTPError as err:
        return None

    return article


def get_links_by_cat(cat_path, start_page, num_pages):
    url = "https://cyberleninka.ru/article/c/" + cat_path

    result = []
    for i in range(start_page, start_page + num_pages):
        response = requests.get(url + "/2")
        response.raise_for_status()

        soup = bs(response.text, 'html.parser')
        result += [a["href"] for a in soup.find('ul', {"class": "list"}).find_all("a")]

    return result


def get_articles_by_cat(cat_path, start_page, num_pages):
    links = get_links_by_cat(cat_path, start_page, num_pages)

    result = []
    for link in links:
        result.append(parse_article(link))

    return result


cats_dict = {
    "Фундаментальная медицина": "basic-medicine",
    "История и археология": "history-and-archaeology",
    "Математика": "mathematics",
    "Механика и машиностроение": "mechanical-engineering",
    "Психологические науки": "psychology"
}

data = []
for cat, path in cats_dict.items():
    data += [[cat, article] for article in get_articles_by_cat(path, 1, 5)]

df = pd.DataFrame(data, columns=["cat", "text"])
df.to_csv("articles.csv", index=False)
