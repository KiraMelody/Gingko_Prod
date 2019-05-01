import re
import math
import textstat
import html2text
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA


def get_img_number(soup):
    '''
    Get the number of image from soup find
    :param soup: BeautifulSoup component build from raw html
    :return: int
    '''
    imgs = soup.find_all('img')
    return len(imgs)

def get_ads_number(soup):
    '''
    Get the number of ads from soup find, according to the images which contains "ads" in its link
    :param soup: BeautifulSoup component build from raw html
    :return: int
    '''
    imgs = soup.find_all('img')
    ads_counter = 0
    for img in imgs:
        if img.has_attr("src") and "ads" in img["src"] :
            ads_counter += 1
    return ads_counter

def get_text(html):
    '''
    Extracts text from html
    :param html: raw html string
    :return: text string
    '''
    h2t = html2text.HTML2Text()
    h2t.no_wrap_links = True
    h2t.ignore_links = True
    h2t.ignore_tables = True
    h2t.ignore_images = True
    h2t.ignore_emphasis = True
    return h2t.handle(html)

def get_reading_level(html):
    '''
    Returns the Flesch-Kincaid Grade of the given text. This is a grade
    formula in that a score of 9.3 means that a ninth grader would be able to
    read the document.
    https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch%E2%80%93Kincaid_grade_level
    :param html: raw html string
    :return: int
    '''
    return textstat.flesch_kincaid_grade(get_text(html))


def get_social_media_score_links(links):
    '''
    Get the social media links from link lists
    :param links: link list
    :return: set of social media links
    '''
    social_media_links = set()
    for link in links:
        if len(link) > 50:
            continue
        if "www.facebook.com" in link or "twitter.com" in link or "www.instagram.com" in link:
            social_media_links.add(link)

    return social_media_links

def get_links(soup):
    '''
    Extract all the links from soup
    :param soup: BeautifulSoup component build from raw html
    :return: link lists
    '''
    links = set()
    for link in soup.findAll('a', attrs={'href': re.compile("^http://")}):
        links.add(link.get('href'))
    for link in soup.findAll('a', attrs={'href': re.compile("^https://")}):
        links.add(link.get('href'))

    return links

def secure_link_ratio(links):
    '''
    Calculate the secure link ratio
    :param links: link list
    :return: float
    '''
    count = 0
    for link in links:
        if "https:" in link:
            count += 1
    if len(links) == 0:
        return 0.0
    return float(count/len(links))

def good_reference_ratio(links):
    '''
    Calculate the good reference ratio of white list link
    :param links: link list
    :return: float
    '''
    good_references = ['nytimes.com', 'wikipedia.org', 'news.yahoo.com', 'news.google.com', 'huffpost.com', 'cnn.com', 'foxnews.com', 'nbcnews.com', 'dailymail.co.uk', 'washingtonpost.com', 'theguardian.com', 'wsj.com', 'abcnews.go.com', 'bbc.com', 'usatoday.com', 'latimes.com']
    count = 0
    for link in links:
        if link in good_references:
            count += 1
    if len(links) == 0:
        return 0.0
    return float(count / len(links))

def social_media_score(soup):
    """
    Crawl links to social media of HTML page and assess the credibility of the website

    Args:
        html_page (str): stringfied html page.
    Returns:
        a float from 0-1 indicating the credibility score based on social media profile
    """
    links = get_links(soup)
    social_media_links = get_social_media_score_links(links)
    # print(social_media_links)
    return round(float(len(social_media_links)/3), 2)

def citation_score(soup):
    """
    Crawl external citations of HTML page
    Assess security of links and compare against a manually curated credible news website set

    Args:
        html_page (str): stringfied html page.
    Returns:
        a float from 0-1 indicating the credibility score based on citation security and credibility
    """
    links = get_links(soup)
    secure_ratio = secure_link_ratio(links)
    ref_ratio = good_reference_ratio(links)
    if ref_ratio == 0.0:
        return  round(secure_ratio, 2)
    else:
        ratio = 1.0 if secure_ratio + ref_ratio > 1.0 else ref_ratio + secure_ratio
        return round(ratio, 2)

def sentiment_analysis(text, full_score=False):
    '''
    Get setiment analisys score from SIA
    :param text: text extracted from raw html
    :param full_score: label of get full score or regular score
    :return: float
    '''
    sia = SIA()
    score = sia.polarity_scores(text)
    if full_score:
        return score
    else:
        x = score['neu'] * 5 - abs(score['neg'] - score['pos'])
        return 1/(1 + math.exp(-x))