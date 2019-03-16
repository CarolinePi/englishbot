import sqlite3


def insert_user_to_users(nickname):
    conn = sqlite3.connect('db.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO users (nickname) VALUES(?)", (nickname,))
    conn.commit()
    conn.close()


def select_from_bd_listenings(complexity):
    conn = sqlite3.connect('db.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM listenings WHERE complexity=(?)",
              [complexity])
    temp = c.fetchall()
    conn.close()
    return temp


def select_from_bd_listening(id):
    conn = sqlite3.connect('db.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM listenings WHERE id=(?)",
              [id])
    temp = c.fetchall()[0]
    conn.close()
    return temp


def insert_user(id_listening, id_user):
    conn = sqlite3.connect('db.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO user_listenings (id_listening, id_user) VALUES(?, ?)",
              (id_listening, id_user))
    conn.commit()
    conn.close()


def check_user(id_listening, id_user):
    conn = sqlite3.connect('db.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM user_listenings WHERE id_listening=(?) AND id_user=(?)",
              (int(id_listening), int(id_user)))
    temp = c.fetchall()
    if len(temp) != 0:
        result = True
    else:
        result = False
    conn.close()
    return result

