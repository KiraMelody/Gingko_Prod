from bs4 import BeautifulSoup
import re

def is_news(html):
	'''
	Naive rule based classifier to filter non-news site
	:param html: raw html
	:return: bool
	'''
	news = re.findall('news', html)
	if len(news) > 5:
		return True
	else:
		return False

def is_valid_url(url):
	'''
	Naive rule nased classifier to filter non-english site
	:param url: string
	:return: bool
	'''
	if url.endswith(('jp', 'ua', 'fr', 'ru', 'ch', 'de', 'be', 'pk', 'ro', 'cn')):
		return False
	else:
		return True