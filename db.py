import sqlite3


def init_database():
    connector = sqlite3.connect("db.db")
    cursor = connector.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS 'users'(user_id TEXT UNIQUE, name TEXT, surname TEXT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 'task_list'
                      (id text, user_id text, number text, time text, text text)""")
    connector.commit()


def add_to_db_users(user_id, name, surname):
    connector = sqlite3.connect("db.db")
    cursor = connector.cursor()
    insert = f"""INSERT INTO 'users'  VALUES ('{user_id}', '{name}', '{surname}')"""
    cursor.execute(insert)
    connector.commit()


def add_to_db_task_list(chat_id, user_id, time, text):  # Функция добавляет данные в таблицу 'task_list'
    connector = sqlite3.connect("db.db")
    cursor = connector.cursor()
    insert = f"""INSERT INTO 'task_list'  VALUES ('{chat_id}', '{user_id}', '{time}', '{text}')"""
    cursor.execute(insert)
    connector.commit()
