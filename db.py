import sqlite3

from StateMachine import States


def init_database():
    connector, cursor = connect()
    cursor.execute("""CREATE TABLE IF NOT EXISTS 'users'(chat_id TEXT UNIQUE, timezone INT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 'task_list'
                      (id text, time text, text text)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 'state'(id text UNIQUE, states text DEFAULT "ZeroState" NOT NULL)""")
    connector.commit()


def connect():
    connector = sqlite3.connect("db.db")
    cursor = connector.cursor()
    return connector, cursor


def add_to_state(chat_id, states):
    connector, cursor = connect()
    a = f"""SELECT count(*) FROM 'state' WHERE id={chat_id}"""
    cursor.execute(a)
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


def add_to_db_users(chat_id, timezone):
    connector, cursor = connect()
    insert = f"""INSERT INTO 'users' VALUES ('{chat_id}',{timezone})"""
    cursor.execute(insert)
    connector.commit()


def get_state(chat_id):
    connector, cursor = connect()
    cursor.execute(f"""SELECT states FROM 'state' WHERE id='{chat_id}'""")
    ce = cursor.fetchone()
    a = States[ce[0]]
    return a


def get_timezone(chat_id):
    connector, cursor = connect()
    cursor.execute(f"""SELECT timezone FROM 'users' WHERE chat_id='{chat_id}'""")
    ce = cursor.fetchone()
    return ce
