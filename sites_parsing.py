import pandas as pd
import re
import ratelim

import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

main_url = 'https://habr.com/ru/post/'
post_count = 10000
parse_df = pd.DataFrame(columns=['num', 'URL', 'Title', 'Post', 'tags', 'hubs'])


def execute_post(page):
    soup = bs(page.text, 'html.parser')

    title = soup.find('meta', property='og:title')
    title = str(title).split('="')[1].split('" ')[0]

    post = str(soup.find('div', id="post-content-body"))
    post = re.sub('\n', ' ', post)
    post = re.sub('\r', ' ', post)
    post = re.sub('<br/>', ' ', post)
    post = re.sub('<b>', ' ', post)
    post = re.sub('</b>', ' ', post)
    post = re.sub('<i>', ' ', post)
    post = re.sub('</i>', ' ', post)
    post = re.sub('<strong>', ' ', post)
    post = re.sub('</strong>', ' ', post)
    post = re.sub('\s+', ' ', post)
    post = re.sub('<a href=.+?">', '', post)
    post = re.sub('<a class=""user_link"" href=".+?">', '', post)
    post = re.sub('<img.+?>', '', post)
    post = re.sub('<.img>', '', post)
    post = re.sub('</a>', '', post)
    post = \
        post.split('article-formatted-body_version-1"><div xmlns="http://www.w3.org/1999/xhtml">')[1].split('</div>')[
            0].strip()

    try:
        tags = list()
        tags_list = soup.find_all('a', attrs={'class': 'tm-tags-list__link'})
        for tag in tags_list:
            tags.append(tag.text)
    except:
        tags = ''

    try:
        hubs = list()
        hubs_list = soup.find_all('a', attrs={'class': 'tm-hubs-list__link'})
        for hub in hubs_list:
            hubs.append(hub.text.strip())
    except:
        hubs = ''

    return title, post, tags, hubs


@ratelim.patient(3, 1)
def get_post(post_num):
    curr_post_url = main_url + str(postNum)

    try:
        response = requests.get(curr_post_url)
        response.raise_for_status()

        response_title, response_post, response_tags, response_hubs = execute_post(response)

        data_list = [post_num, curr_post_url, response_title, response_post, response_tags, response_hubs]
        parse_df.loc[len(parse_df)] = data_list

    except requests.exceptions.HTTPError as err:
        pass


if __name__ == "__main__":
    for pc in tqdm(range(10)):
        postNum = pc + 1
        get_post(postNum)

    parse_df.to_csv("parsed_articles.csv", index=False)
