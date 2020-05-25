import sqlite3

from src.state_machine import States


def init_database():
    connector, cursor = connect()
    cursor.execute("""CREATE TABLE IF NOT EXISTS 'users'(chat_id TEXT UNIQUE, timezone INT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 'task_list'
                      (id TEXT, time INT, text TEXT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 'state'(id text UNIQUE, states text DEFAULT "ZeroState" NOT NULL)""")
    connector.commit()


def connect():
    connector = sqlite3.connect("db.db")
    cursor = connector.cursor()
    return connector, cursor


def update_state(chat_id, states):
    connector, cursor = connect()
    count = f"""SELECT count(*) FROM 'state' WHERE id=('{chat_id}')"""
    cursor.execute(count)
    count = cursor.fetchone()
    if count[0] == 0:
        insert = f"""INSERT INTO 'state' (id) VALUES ('{chat_id}')"""
        cursor.execute(insert)
    update = f"""UPDATE 'state' SET states = '{states.name}' WHERE id = ('{chat_id}')"""
    cursor.execute(update)
    connector.commit()


def add_to_db_task_list(chat_id, time, text):  # Функция добавляет данные в таблицу 'task_list'
    connector, cursor = connect()
    insert = f"""INSERT INTO 'task_list'  VALUES ('{chat_id}', '{time}', '{text}')"""
    cursor.execute(insert)
    connector.commit()


def add_to_db_users(chat_id, timezone):  # Функция добавляет данные в таблицу 'users'
    connector, cursor = connect()
    insert = f"""INSERT INTO 'users' VALUES ('{chat_id}',{timezone})"""
    cursor.execute(insert)
    connector.commit()


def get_state(chat_id):  # Функция получает данные поля states таблицы state
    connector, cursor = connect()
    cursor.execute(f"""SELECT states FROM 'state' WHERE id='{chat_id}'""")
    temp = cursor.fetchone()
    state = States[temp[0]]
    return state


def get_task(chat_id):  # Функция получает данные поля text таблицы task_list
    connector, cursor = connect()
    cursor.execute(f"""SELECT text FROM 'task_list' WHERE id='{chat_id}'""")
    temp = cursor.fetchone()
    if not temp:
        return None
    else:
        text = temp[0]
        return text


def delete_task(chat_id, first):
    connector, cursor = connect()
    delete = f"""DELETE FROM 'task_list' WHERE text = '{first}' """
    cursor.execute(delete)
    connector.commit()


def get_timezone(chat_id):  # Функция получает данные поля timezone таблицы users
    connector, cursor = connect()
    cursor.execute(f"""SELECT timezone FROM 'users' WHERE chat_id='{chat_id}'""")
    temp = cursor.fetchone()
    if not temp:
        return
    else:
        timezone = temp[0]
        return timezone
