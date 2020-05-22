import sqlite3

from StateMachine import States


def init_database():
    connector = sqlite3.connect("db.db")
    cursor = connector.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS 'users'(user_id TEXT UNIQUE, name TEXT, surname TEXT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 'task_list'
                      (id text, user_id text, time text, text text)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 'state'(id text UNIQUE, states text DEFAULT "ZeroState" NOT NULL)""")
    connector.commit()


def add_to_state(chat_id, states):
    connector = sqlite3.connect("db.db")
    cursor = connector.cursor()
    a = f"""SELECT count(*) FROM 'state' WHERE id={chat_id}"""
    cursor.execute(a)
    count = cursor.fetchone()
    if count[0] == 0:
        insert = f"""INSERT INTO 'state' (id) VALUES ('{chat_id}')"""
        cursor.execute(insert)
    update = f"""UPDATE 'state' SET states = '{states.name}' WHERE id = ('{chat_id}')"""
    cursor.execute(update)
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


def get_state(chat_id):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    cursor.execute(f"""SELECT states FROM 'state' WHERE id='{chat_id}'""")
    ce = cursor.fetchone()
    a = States[ce[0]]
    return a
