import configparser
from datetime import timezone, timedelta, time
from dataclasses import dataclass, field



def get_work_period(minutes):
	seconds = int(minutes) * 60
	return seconds


class Config:
	days = {
		"понедельник": 0,
		"вторник": 1,
		"среда": 2,
		"четверг": 3,
		"пятница": 4,
		"суббота": 5,
		"воскресенье": 6
		}
	
	
	def __init__(self):
		conf = configparser.ConfigParser()
		conf.read('config - NEWS.ini', encoding='utf-8')
		self.bot_token = conf.get('DEFAULT', 'bot_token')
		self.channels_id = list(map(lambda x: int(x), conf.get('DEFAULT', 'channels_id').split(", ")))
		self.admins = list(map(lambda x: int(x), conf.get('DEFAULT', 'admins').split(", ")))
		
		self.proxies = list(map(lambda b: b.split("="), conf.get('PROXY', 'proxies').split(", ")))
		
		self.work_days = list(map(lambda x: self.days[x], conf.get('SETTINGS', 'work_days').split(", ")))
		self.work_period = get_work_period(conf.get('SETTINGS', 'work_period'))
		
		self.timezone = timezone(timedelta(hours=3))
		
		
		if self.timezone:
			start_hours, start_minutes = conf.get('SETTINGS', 'work_start_time').split(":")
			self.work_start_time = time(hour=int(start_hours), minute=int(start_minutes), tzinfo=self.timezone)
			
			end_hours, end_minutes = conf.get('SETTINGS', 'work_end_time').split(":")
			self.work_end_time = time(hour=int(end_hours), minute=int(end_minutes), tzinfo=self.timezone)
		
		self.work_time = [
			time(hour=int(hour_time), minute=int(minute_time))
			for hour_time, minute_time in list(map(lambda x: x.split(":"), conf.get('SETTINGS', 'work_time').split(", ")))]
		self.work_time.sort()
		
		
		self.urls = []
		with open("URLS.txt", "r", encoding="utf-8") as f:
			lines = f.readlines()
			for line in lines:
				self.urls.append(list(map(lambda x: x.replace("\n", ""), line.split(", "))))
		
		
		self.hashtag = conf.get('MESSAGE', 'hashtag')
		self.text = conf.get('MESSAGE', 'text')
		self.length_text = conf.get('MESSAGE', 'text_length')
		
		
		
		if self.hashtag == "on":
			self.hashtag = True
		else:
			self.hashtag = False
			
		if self.length_text == "*":
			self.length_text = 1000
		else:
			self.length_text = int(self.length_text)
		
		if self.proxies == "off":
			self.proxies = False


@dataclass
class Post:
	id: int
	href: str
	title: str
	text: str
	hashtags: field(default_factory=list)
	
	

