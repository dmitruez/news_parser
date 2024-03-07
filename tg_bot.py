import telebot
from entities import Post
from telebot import types




def send_post(config, post: Post):
	bot_token = config.bot_token
	channels = config.channels_id,
	hashtag = config.hashtag
	text_p = config.text
	text_lenght = config.length_text
	bot = telebot.TeleBot(token=bot_token, parse_mode="html")
	
	
	url_buttons = [types.InlineKeyboardButton(text=name, url=url) for url, name in config.urls]
	markup = types.InlineKeyboardMarkup()
	for button in url_buttons:
		markup.add(button)
	
	if text_lenght == 1000:
		sclicing = slice(None, None, None)
		ending = ''
	else:
		sclicing = slice(None, text_lenght, None)
		ending = "..."
	for channel in channels:
		if hashtag:
			bot.send_message(chat_id=channel[0],
			                 text=f"{post.hashtags}\n<b>{post.title}</b>\n\n{post.text[sclicing]}{ending}\n\n<i"
			                      f">{text_p}</i>", reply_markup=markup)
		else:
			bot.send_message(
				chat_id=channel[0],
				text=f"<b>{post.title}</b>\n\n{post.text[sclicing]}{ending}\n\n<i>{text_p}</i>", reply_markup=markup
				)
