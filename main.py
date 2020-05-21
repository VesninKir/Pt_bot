import telebot
from telebot import types

import config
from db import init_database

bot = telebot.TeleBot(config.token)

start_keyboard = types.ReplyKeyboardMarkup(True, True)
btn1 = types.KeyboardButton('Новое напоминание')
start_keyboard.add(btn1)


@bot.message_handler(commands=["start"])
def start_answer(message):
    bot.send_message(message.chat.id, 'Привет, я помогу тебе вспомнить всё', reply_markup=start_keyboard)


@bot.message_handler(content_types=["text"])
def fill_database(message):
    chat_id = message.chat.id
    if message.text == 'Новое напоминание':
        bot.send_message(chat_id, "Enter time")
        t = input()


if __name__ == '__main__':
    init_database()
    bot.infinity_polling()
