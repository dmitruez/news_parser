import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime


def get_hashtags(string: str):
	all_words = string.split("#")
	not_allowed_words = ['+', '!', '$', '%', '-', '^', '&', '*', '?', '/', ':', '№']
	hashtags = ""
	for word in all_words[1:]:
		hashtags += "#" + word.replace(" ", "").replace("-", "") + ", "
	
	for word in not_allowed_words:
		hashtags = hashtags.replace(word, '')
	
	res = hashtags[:-2]
	return res


class Parser:
	URL = "https://forklog.com/news"
	
	last_proxie = None
	
	@classmethod
	def get_page(cls, proxies):
		session = requests.Session()
		full_proxies = [{transfer: proxy} for transfer, proxy in proxies]
		for proxy in full_proxies:
			if proxy != cls.last_proxie:
				cls.last_proxie = proxy
				session.proxies = proxy
				html = session.get(cls.URL)
				soup = BeautifulSoup(html.content, 'html.parser')
				return soup
	
	@staticmethod
	def get_page_by_href(div):
		href = div.find("a")["href"]
		page_sours = requests.get(href)
		page_soup = BeautifulSoup(page_sours.content, 'html.parser')
		return page_soup, href
	
	@staticmethod
	def filter_p_names(element):
		if element.find("blockquote"):
			return False
		else:
			if element.attrs:
				return False
			return True
	
	
	@staticmethod
	def filter_text(text: str):
		a = text.replace('Подписывайтесь на ForkLog в социальных сетях', '')
		d = a.replace('Рассылки ForkLog: держите руку на пульсе биткоин-индустрии!', '')
		while d.count("..") > 0:
			d = d.replace('..', '.')
		while d.count(". .") > 0:
			d = d.replace('. .', '.')
		while d.count("\n\n") > 0:
			d = d.replace("\n\n", '')
		while d.count(":.") > 0:
			d = d.replace(":.", ':')
		while d.count(". \n.") > 0:
			d = d.replace(". \n.", '')
		return d[:-1]
	
	
	
	def create_text(self, array):
		text = ''
		for elem in array:
			if len(elem) > 10:
				try:
					for sentence in elem.split("."):
						if len(sentence) > 10:
							if len(text) < 1000:
								text += sentence + "."
								if len(text) > 1000:
									res = text.replace(sentence + ".", "")
									filtred_res = self.filter_text(res)
									return filtred_res
					text += "\n"
				except Exception as e:
					print(e)
		filtred_text = self.filter_text(text)
		return filtred_text
	
	def run(self, database, proxies):
		soup = self.get_page(proxies)
		while True:
			try:
				item = soup.find("div", class_="cell")
				page_soup, href = self.get_page_by_href(item)
				
				
				content = page_soup.find("div", class_="post_content")
				p_class = content.find_all("p")
				all1 = list(filter(self.filter_p_names, p_class))
				
				
				title = content.find("h1").text
				text = self.create_text(list(map(lambda x: x.text, all1)))
				hashtags = get_hashtags(content.find("div", class_="post_tags_top").text)
				database.insert(href, title, text, hashtags)
				break
			except:
				logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Не получилось найти пост")
			
