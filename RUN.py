import logging
from datetime import datetime
from time import sleep

import telebot
from telebot.types import Message, CallbackQuery
from telebot import types

from entities import Config
from functions import Runner, stop, send_to_telegram


a = Config()
admins = a.admins
r = Runner()
bot_token = "6922074672:AAFQV43J_1YPp08FLj67P4FmWlkqMFky-kM"
bot = telebot.TeleBot(token=bot_token, parse_mode="html")


def add_admin_handler(message: Message):
	try:
		admins.append(int(message.text))
		bot.send_message(message.chat.id, "Добавлен новый админ")
	except Exception:
		bot.send_message(message.chat.id, "Не правильно введен id пользователя")





@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
	if message.from_user.id in admins:
		bot.send_message(message.chat.id, f"Бот начал свою работу")
		logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Поступила команда на старт парсинга")
		r.run()


@bot.message_handler(commands=['stop'])
def stop_script(message: Message):
	if message.from_user.id in admins:
		bot.send_message(message.chat.id, f"Бот остановил свою работу")
		logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Поступила команда на завершение работы парсинга")
		stop()


@bot.message_handler(commands=['restart'])
def restart_script(message: Message):
	if message.from_user.id in admins:
		bot.send_message(message.chat.id, "Бот перезапускается")
		logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Стартовал перезапуск")
		stop()
		sleep(3)
		bot.send_message(message.chat.id, f"Бот начал свою работу")
		logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Поступила команда на старт парсинга")
		r.run()



@bot.message_handler(commands=['post'])
def posting_script(message: Message):
	if message.from_user.id in admins:
		bot.send_message(message.chat.id, "Бот вне времени запускает парсер")
		logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Поступила команда на одноразовый парсинг")
		send_to_telegram()





@bot.message_handler(commands=['clear_bd'])
def clear_bd(message: Message):
	if message.from_user.id in admins:
		bot.send_message(message.chat.id, f"База данных очищена")
		logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Поступила команда полной очистки базы данных")
		r.clear_bd()
		


@bot.message_handler(commands=['add_admin'])
def add_admin(message: Message):
	if message.from_user.id in admins:
		msg = bot.send_message(message.chat.id, "Введите id пользователя")
		bot.register_next_step_handler(msg, add_admin_handler)



@bot.message_handler(commands=['del_admin'])
def add_admin(message: Message):
	admin_buttons = [types.InlineKeyboardButton(name, callback_data=str(name)) for name in admins]
	markup = types.InlineKeyboardMarkup()
	for button in admin_buttons:
		markup.add(button)
	if message.from_user.id in admins:
		bot.send_message(message.chat.id, "Какого админа вы хотите убрать?", reply_markup=markup)



@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler1(call: CallbackQuery):
	try:
		admins.remove(int(call.data))
		bot.send_message(call.message.chat.id, "Админ успешно убран")
	except Exception:
		bot.send_message(call.message.chat.id, "Такого админа уже не существует")



if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO)
	bot.infinity_polling()