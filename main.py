import datetime
import config
import re

import telebot
from telebot import types
from src.db import init_database, add_to_db_task_list, update_state, get_state, add_to_db_users, get_timezone, get_task, \
    delete_task
from src.state_machine import States
from threading import Timer

bot = telebot.TeleBot(config.TOKEN)

start_keyboard = types.ReplyKeyboardMarkup(True, True)
new_reminder_button = types.KeyboardButton('Новое напоминание')
start_keyboard.add(new_reminder_button)

alarm_time = 0
time_pattern = re.compile(r'(?P<time>\d+:\d+) ')
day_pattern = re.compile(r' (?P<day>.*)')
task_name = ''


@bot.message_handler(commands=["start"])  # Обработчик команды start
def start_answer(message):
    if get_timezone(message.chat.id) is not None:
        bot.send_message(message.chat.id, 'Привет, я помогу тебе вспомнить всё.\n', reply_markup=start_keyboard)
    else:
        bot.send_message(message.chat.id, 'Привет, я помогу тебе вспомнить всё.\n'
                                          'Для начала работы введите Вашу временную зону относительно GMT+0: \n')
        update_state(message.chat.id, States.State_SetTimezone)


# Проверка состояния, установка временной зоны
@bot.message_handler(func=lambda message: get_state(message.chat.id) in [States.State_SetTimezone])
def fill_db(message):
    clear_str = message.text.lower()
    clear_str = clear_str.replace('gmt', '')
    try:
        value = int(clear_str)
    except AttributeError:
        bot.send_message(message.chat.id, 'Введено неверное число! Попробуйте еще!')
        return
    update_state(message.chat.id, States.Start_state)
    add_to_db_users(message.chat.id, value)
    bot.send_message(message.chat.id, 'Временная зона установлена!', reply_markup=start_keyboard)


def notification(chat_id):
    bot.send_message(chat_id, 'Напоминаю о " ' + get_task(chat_id) + '"')
    delete_task(chat_id, get_task(chat_id))


@bot.message_handler(func=lambda message: message.text == "Новое напоминание")  # Проверка состояния времени и ввод
def reminders_start(message):
    update_state(message.chat.id, States.State_SetTime)
    bot.send_message(message.chat.id, 'Введите время в GMT+0\n'
                                      'Формат ввода: H:M D.M.Y\n')


def parse_time(text):
    time_ = time_pattern.search(text).group('time')
    day_ = day_pattern.search(text).group('day')
    time_ = time_.split(':')
    day_ = day_.split('.')
    time_ = [f"0{value}" if len(value) == 1 else value for value in time_]
    day_ = [f"0{value}" if len(value) == 1 else value for value in day_]
    parsed_time = ':'.join(time_)
    parsed_day = '.'.join(day_)
    return f"{parsed_time} {parsed_day}"


@bot.message_handler(
    func=lambda message: get_state(message.chat.id) in [States.State_SetTime])  # Проверка состояния, введение времени
def set_time(message):
    global time, alarm_time
    time = parse_time(message.text)
    value = datetime.datetime.strptime(time, '%H:%M %d.%m.%Y')
    delta = datetime.timedelta(hours=get_timezone(message.chat.id))
    value -= delta
    server_time_now = datetime.timedelta(hours=7)
    time_now = datetime.datetime.now() - server_time_now
    if time_now > value:
        keyboard = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text="Назад в 2007!", url="https://www.youtube.com/watch?v=pcr8kBeA_kE")
        keyboard.add(url_button)
        bot.send_message(message.chat.id, "Кажется, кто-то хочет вернуться в прошлое?\n"
                                          "Можем попробовать. Или введи корректную дату в будущем.",
                         reply_markup=keyboard)
        return

    update_state(message.chat.id, States.State_SetText)
    alarm_time = int(value.timestamp() - time_now.timestamp())
    bot.send_message(message.chat.id, alarm_time)
    bot.send_message(message.chat.id, "Введите текст напоминания:", time)


@bot.message_handler(func=lambda message: get_state(message.chat.id) in [States.State_SetText])  # Проверка состояния,
# введение напоминания. Занесение данных в базу
def set_text(message):
    global task_name, time
    task_name = message.text
    update_state(message.chat.id, States.State_Done)
    add_to_db_task_list(message.chat.id, time, task_name)
    bot.send_message(message.chat.id, "Готово! Я напомню вам о " + task_name)
    timer = Timer(alarm_time, notification, [message.chat.id])
    timer.start()


@bot.message_handler(content_types=["text"])  # Проверка на введенный с клавиатуры текст вне ключевых состояний
def default_response(message):
    if message.text == 'Привет':
        bot.send_message(message.chat.id, "Привет!", reply_markup=start_keyboard)
    else:
        bot.send_message(message.chat.id, "Я вас не понимаю, воспользуйтесь клавиатурой:", reply_markup=start_keyboard)


if __name__ == '__main__':
    init_database()
    bot.infinity_polling(True, True)  # Общение с ботом
