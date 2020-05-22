import telebot
from telebot import types

import config
from StateMachine import States
from db import init_database, add_to_db_task_list, add_to_state, get_state

bot = telebot.TeleBot(config.token)

start_keyboard = types.ReplyKeyboardMarkup(True, True)
btn1 = types.KeyboardButton('Новое напоминание')
start_keyboard.add(btn1)

time = ''
task_name = ''


@bot.message_handler(commands=["start"])
def start_answer(message):
    bot.send_message(message.chat.id, 'Привет, я помогу тебе вспомнить всё', reply_markup=start_keyboard)


def set_state(chat_id, state_name):
    add_to_state(chat_id, state_name)


@bot.message_handler(func=lambda message: message.text == "Новое напоминание")
def check(message):
    set_state(message.chat.id, States.State_SetTime)
    bot.send_message(message.chat.id, 'Введите время:')


def check_state_stat(message):
    return get_state(message.chat.id) == States.State_SetTime


@bot.message_handler(func=lambda message: check_state_stat(message))
def Set_Time(message):
    global time
    set_state(message.chat.id, States.State_SetText)
    time = message.text
    bot.send_message(message.chat.id, "Введите текст напоминания:", time)


@bot.message_handler(func=lambda message: get_state(message.chat.id) in [States.State_SetText])
def Set_Text(message):
    global task_name
    set_state(message.chat.id, States.State_SetText)
    task_name = message.text
    set_state(message.chat.id, States.State_Done)
    bot.send_message(message.chat.id, "Готово! Я напомню вам о " + task_name + " в " + time)
    add_to_db_task_list(message.chat.id, '', time, task_name)


@bot.message_handler(func=lambda message: get_state(message.chat.id) in [States.State_Done])
def Fill_DB(message):
    global time, task_name
    set_state(message.chat.id, States.Start_state)


if __name__ == '__main__':
    init_database()
    bot.infinity_polling()
