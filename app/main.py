#!/usr/bin/env python
# coding: utf-8

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from cachelib import SimpleCache
import urllib.request
import urllib.error
import urllib.parse
from bs4 import BeautifulSoup, SoupStrainer
import re
import random
from app.helpers import randomstring, censor


CACHE_TIMEOUT = 60*60  # seconds
KW_LEN = 3  # Random search keyword length
MIN_LEN = 8  # Sentence min word count
MAX_LEN = 20  # Sentence max word count
SCH_INTERVAL = 30  # Minutes - how often to fetch sentences and refill cache

app = Flask(__name__)
cache = SimpleCache()
scheduler = BackgroundScheduler(daemon=True)

#  Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


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
    headers = {'User-Agent' : user_agent, 'Referer' : referer}
    req = urllib.request.Request(url, None, headers)
    try:
        response = urllib.request.urlopen(req)
        return response.read()
    except urllib.error.HTTPError as er:
        print("Error Code :{} ".format(er.code))
        return None


def get_sentences(textdata):
    """
    Perform regex match to match and return a random sentence. Sentences with word count between min_len and max_len are returned.

        Parameters:
            textdata (str): Text on which to perform regex match

        Returns:
            slist (list): list of sentence strings
    """

    pattern = re.compile(r'([A-Z][a-z, "]*[\.!?])')
    sentences = re.findall(pattern, textdata)

    slist = [s for s in sentences
             if len(s.split()) >= MIN_LEN
             and len(s.split()) <= MAX_LEN]
    return slist


def ddg(kw):
    """
    perform a duckduckgo search of a random string

        Parameters:
            kw (str): Search keyword
        Return:
            html(str): utf-8 decoded html
    """
    ddg_url = "https://duckduckgo.com/?q={}+f:htm".format(kw)
    return fetch_html(ddg_url).decode('utf-8')


def internet_profundity(count=50):
    """
    Scrap ddg search with a random string.

        Parameters:

        Returns:
            censored_list (list): Returns a list of censored sentences

    """
    html = ddg(randomstring(KW_LEN))
    soup_strainer = SoupStrainer('a', {'class': 'result__a'}, href=True)
    soup = BeautifulSoup(html,  "html.parser", parse_only=soup_strainer)

    links = []
    for link in soup:
        href = link['href']
        p1 = urllib.parse.urlparse(href)
        p2 = urllib.parse.parse_qs(p1.query)
        links.append(p2['uddg'][0])

    unsensored_sentences = []
    while len(unsensored_sentences) < count:
        # select a random url from links
        url_next = random.choice(links)
        html_next = fetch_html(url_next)
        soup = BeautifulSoup(html_next, "html.parser")
        unsensored_sentences += get_sentences(soup.get_text())

    censored_list = [censor(s) for s in unsensored_sentences]
    return censored_list


def fill_cache():
    """
    Cache the results
        Parameters:

        Returns:
            censored_list (list): Returns a list of censored sentences
    """
    print("Filling cache")
    censored_list = internet_profundity()
    cache.set('sentences', censored_list, timeout=CACHE_TIMEOUT)
    return censored_list


fill_cache()  # Fill cache for the first time

scheduler.add_job(fill_cache, trigger='interval', minutes=SCH_INTERVAL)
scheduler.start()


@app.route("/cached")
def cache_view():
    sentences = cache.get('sentences')
    if sentences is None:
        sentences = fill_cache()
    response = "\n".join(sentences)
    return f"<em>{response}</em>"


@app.route("/")
def home_view():
    sentences = cache.get('sentences')
    if sentences is None:
        sentences = fill_cache()
    response = random.choice(sentences)
    return f"<em>{response}</em>"

