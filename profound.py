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
    """accepts url and fetches content"""
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13 (.NET CLR 3.5.30729)'
    referer = 'http://www.google.com'
    headers = { 'User-Agent' : user_agent, 'Referer' : referer }
    req = urllib.request.Request(url, None, headers)
    try:
        response = urllib.request.urlopen(req)
        return response.read()
    except urllib.error.HTTPError as er:
        print("error code :{} ".format(er.code))
        return None
    
def get_sentence(textdata):
    #regex match all sentences
    pattern = re.compile(r'([A-Z][a-z, "]*[\.!?])')
    sentences = re.findall(pattern, textdata)
    #get only sentences that are >= 8 words and <=20
    slist = [s for s in sentences if len(s.split()) >= 8 and len(s.split()) <= 20 ] 
    #return random item
    return random.choice(slist)


def ddg(kw):
    """perform a duckduckgo search of a random string"""
    ddg_url="https://duckduckgo.com/?q={}+f:htm".format(kw)
    return fetch_html(ddg_url).decode('utf-8')
    

def internet_profundity():
    html = ddg(randomstring(3))
    soup = BeautifulSoup(html,  "html.parser", parse_only=SoupStrainer('a', {'class': 'result__a'}, href=True))

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
    jk = censor(get_sentence(soup.get_text()))
    print(f'"{jk}"\n\t\t~ {url_next}')



if __name__ == "__main__":
    while True:
        try:
            internet_profundity()
            break
        except:
            print(random.choice(['The internet refuses to speak... ¯\_(ツ)_/¯', 'The internet is silent...']))
