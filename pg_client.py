import psycopg2
from psycopg2.errors import UniqueViolation
from entities import Post
import logging
from datetime import datetime


class PgDataBase:
	db_password = 'postgres'
	db_user = 'postgres'
	db_host = 'localhost'
	db_port = '5432'
	
	
	def __init__(self):
		self.connection = psycopg2.connect(
			user=self.db_user,
			password=self.db_password,
			host=self.db_host,
			port=self.db_port,
			)
		self.cursor = self.connection.cursor()
		self._create_table()
		try:
			self.last_pars = self.get_last_post().title
		except IndexError:
			self.last_pars = None
	
	def _create_table(self):
		self.cursor.execute(
			f"""
				CREATE TABLE IF NOT EXISTS bit_news
				(
					id serial PRIMARY KEY,
					href varchar(200) UNIQUE,
					title text,
					text text,
					hashtags text
				)
			"""
			)
		self.connection.commit()
	
	def insert(self, href, title, text, hashtags):
		try:
			self.cursor.execute(
				f"""
				INSERT INTO bit_news (href, title, text, hashtags)
				VALUES (%s, %s, %s, %s)
				""", (href, title, text, hashtags)
				)
			self.connection.commit()
			logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- В базу данных добавлен новый пост")
		except UniqueViolation:
			logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- В базу данных поступил уже существующий пост")
			self.connection.rollback()
	
	def delete_all_rows(self):
		self.cursor.execute(
			f"""
			DELETE FROM bit_news
			"""
			)
		self.connection.commit()
	
	def get_last_post(self):
		self.cursor.execute(
			f"""
			SELECT * FROM bit_news
			"""
			)
		id, href, title, text, hashtags = self.cursor.fetchall()[-1]
		post = Post(id, href, title, text, hashtags)
		return post


