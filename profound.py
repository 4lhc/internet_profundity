#!/usr/bin/env python
# coding: utf-8

import urllib.request
import urllib.error
import urllib.parse
from bs4 import BeautifulSoup, SoupStrainer
import re
import random
from helpers import randomstring, censor


def fetch_html(url):
    """
    Returns html content

        Parameters:
            url (str): URL string

        Returns:
            html (bytes): If successfully got response
            None: If failed to get response
    """

    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13 (.NET CLR 3.5.30729)'
    referer = 'http://www.duckduckgo.com'
    headers = { 'User-Agent' : user_agent, 'Referer' : referer }
    req = urllib.request.Request(url, None, headers)
    try:
        response = urllib.request.urlopen(req)
        return response.read()
    except urllib.error.HTTPError as er:
        print("Error Code :{} ".format(er.code))
        return None

def get_sentence(textdata):
    """
    Perform regex match to match and return a random sentence. Sentences with word count between min_len and max_len are returned.

        Parameters:
            textdata (str): Text on which to perform regex match

        Returns:
            sentence (str):
    """
    min_len = 8
    max_len = 20

    pattern = re.compile(r'([A-Z][a-z, "]*[\.!?])')
    sentences = re.findall(pattern, textdata)

    slist = [s for s in sentences
            if len(s.split()) >= min_len
            and len(s.split()) <= max_len]
    return random.choice(slist)


def ddg(kw):
    """
    perform a duckduckgo search of a random string

        Parameters:
            kw (str): Search keyword
        Return:
            html(str): utf-8 decoded html
    """
    ddg_url="https://duckduckgo.com/?q={}+f:htm".format(kw)
    return fetch_html(ddg_url).decode('utf-8')


def internet_profundity(source=True):
    """
    Scrap ddg search with a random string.

        Parameters:
            source (bool): If True, return the source url too.

        Returns:
            profound (str): Returns a sentence

    """
    kw_len = 3
    html = ddg(randomstring(kw_len))
    soup_strainer = SoupStrainer('a', {'class': 'result__a'}, href=True)
    soup = BeautifulSoup(html,  "html.parser", parse_only=soup_strainer)

    links = []
    for link in soup:
        href = link['href']
        p1 = urllib.parse.urlparse(href)
        p2 = urllib.parse.parse_qs(p1.query)
        links.append(p2['uddg'][0])

    #select a random url from links
    url_next = random.choice(links)


    html_next = fetch_html(url_next)
    soup = BeautifulSoup(html_next, "html.parser")
    absurdity = censor(get_sentence(soup.get_text()))
    if source:
        absurdity = f'"{absurdity}"\n\t\t~ {url_next}'

    return f'"{absurdity}"'


if __name__ == "__main__":
    while True:
        try:
            print(internet_profundity(source=False))
            break
        except:
            print(random.choice(['The internet refuses to speak... ¯\_(ツ)_/¯',
                                 'The internet is silent...']))
