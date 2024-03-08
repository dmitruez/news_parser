from datetime import time, datetime, timedelta
from entities import Config
import schedule
import tg_bot
from time import sleep
from parser import Parser
from pg_client import PgDataBase
import logging

database = PgDataBase()


def get_time(datetime_now: datetime,  config: Config, time_: time = None) -> timedelta:
	if time_ is None:
		hour, minute = get_timedelta(config.work_period)
		hours = datetime_now.hour + hour
		minutes = datetime_now.minute + minute
		new_start_time = timedelta(hours=hours, minutes=minutes, seconds=1)
	else:
		hours = time_.hour
		minutes = time_.minute
		new_start_time = timedelta(hours=hours, minutes=minutes, seconds=1)
	return new_start_time
	


def get_timedelta(seconds: int) -> [int]:
	minutes, sec = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	return hours, minutes



def send_to_telegram():
	config = Config()
	parser = Parser()
	if config.proxies:
		parser.run(database, config.proxies)
	else:
		parser.run(database, config.proxies)
	post = database.get_last_post()
	if post.title == database.last_pars:
		post = None
		logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Пост повторяется | {database.last_pars}")
	else:
		logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Отправляем новый пост  в тг каналы | {post.title}")
	if post is not None:
		tg_bot.send_post(config, post)
		database.last_pars = post.title
	next_pars = schedule.get_jobs()[0].next_run
	logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Следующий парсинг в {next_pars}")
	
	
	
def run_parser(event):
	global end
	end = False
	config = Config()
	start_time = config.work_start_time
	end_time = config.work_end_time
	work_days = config.work_days
	schedule.every(config.work_period).seconds.do(send_to_telegram)
	work_times = config.work_time
	send_to_telegram()
	while True:
		if end:
			return
		dt = datetime.now(tz=config.timezone)
		today = dt.weekday()
		time_now = time(hour=dt.hour, minute=dt.minute, tzinfo=config.timezone)
		nex_pars = get_time(dt, config)
		timers = [get_time(dt, config, work_time) - timedelta(seconds=1) for work_time in work_times]
		if today in work_days:
			if start_time < time_now < end_time:
				for timer in timers:
					if get_time(dt, config, time(dt.hour, dt.minute)) > timer:
						pass
					else:
						if nex_pars > timer:
							logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Ждем запланированный парсинг")
							while True:
								dt = datetime.now(tz=config.timezone)
								if timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second + 1)  > timer:
									schedule.clear()
									schedule.every(config.work_period).seconds.do(send_to_telegram)
									
									logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Запланированный парсинг выполнен")
									next_pars = schedule.get_jobs()[0].next_run
									logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Следующий парсинг в {next_pars}")
									send_to_telegram()
									break
								sleep(1)
								
				schedule.run_pending()
				sleep(1)
			else:
				sleep(10)
		else:
			sleep(10)
	
	
def clear_bd():
	database.delete_all_rows()
	database.last_pars = None
	logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- База данных очищена")
		
		
def stop():
	global end
	end = True
	schedule.clear()
	logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Парсинг остановлен")



