import datetime
import re
import subprocess

import telebot
from telebot import types

import config
from StateMachine import States
from db import init_database, add_to_db_task_list, add_to_state, get_state, add_to_db_users, get_timezone

bot = telebot.TeleBot(config.token)

start_keyboard = types.ReplyKeyboardMarkup(True, True)
btn1 = types.KeyboardButton('Новое напоминание')
start_keyboard.add(btn1)

time = ''
task_name = ''


@bot.message_handler(commands=["start"])
def start_answer(message):
    if get_timezone(message.chat.id) is not None:
        bot.send_message(message.chat.id, 'Привет, я помогу тебе вспомнить всё.\n', reply_markup=start_keyboard)
    else:
        bot.send_message(message.chat.id, 'Привет, я помогу тебе вспомнить всё.\n'
                                          'Для начала работы введите Вашу временную зону: \n')
        set_state(message.chat.id, States.State_SetTimezone)


@bot.message_handler(func=lambda message: get_state(message.chat.id) in [States.State_SetTimezone])
def Fill_DB(message):
    value = 0
    str = message.text.lower()
    str = str.replace('gmt', '')
    str = str.replace('мск', '')
    try:
        value = int(str)
    except:
        bot.send_message(message.chat.id, 'Введено неверное число! Попробуйте еще!')
        return
    set_state(message.chat.id, States.Start_state)
    add_to_db_users(message.chat.id, value)
    bot.send_message(message.chat.id, 'Временная зона установлена!', reply_markup=start_keyboard)


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
    value = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    delta = datetime.timedelta(hours=get_timezone(message.chat.id))

    time = value.timestamp()
    bot.send_message(message.chat.id, "Введите текст напоминания:", time)


@bot.message_handler(func=lambda message: get_state(message.chat.id) in [States.State_SetText])
def Set_Text(message):
    global task_name, time
    set_state(message.chat.id, States.State_SetText)
    task_name = message.text
    set_state(message.chat.id, States.State_Done)
    bot.send_message(message.chat.id, "Готово! Я напомню вам о " + task_name)
    add_to_db_task_list(message.chat.id, time, task_name)


def add_task(chat_id, text, time):
    cmd = f"""echo "{config.sdir} {chat_id}  \'{text}\'" | at {time}"""
    out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = str(out.communicate())
    number = re.search('job(.+?) at', stdout).group(1)


@bot.message_handler(content_types=["text"])
def unknown(message):
    if message.text == 'Привет':
        bot.send_message(message.chat.id, "Привет!", reply_markup=start_keyboard)
    else:
        bot.send_message(message.chat.id, "Я вас не понимаю, воспользуйтесь клавиатурой:", reply_markup=start_keyboard)





if __name__ == '__main__':
    init_database()
    bot.infinity_polling(True, True)
