import sqlite3
import json
import os

DB_FILE = 'notenrechner.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_storage 
                 (username TEXT PRIMARY KEY, data TEXT)''')
    conn.commit()
    conn.close()

def save_data(username, data_dict):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    json_data = json.dumps(data_dict)
    c.execute("INSERT OR REPLACE INTO user_storage (username, data) VALUES (?, ?)", 
              (username, json_data))
    conn.commit()
    conn.close()

def load_data(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT data FROM user_storage WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return {}