import sqlite3
import json
import streamlit as st
from webdav4.client import Client

DB_FILE = 'notenrechner.db'

def sync_to_switchdrive():
    """Lädt die lokale Datenbank-Datei automatisch hoch."""
    try:
        client = Client(
            base_url=st.secrets["webdav"]["hostname"],
            auth=(st.secrets["webdav"]["username"], st.secrets["webdav"]["password"])
        )
        # Upload der Datei
        client.upload_file(
            local_path=DB_FILE, 
            to_path="notenrechner_backup.db", 
            overwrite=True
        )
        return True
    except Exception:
        # Im Automatik-Modus loggen wir Fehler eher dezent in der Konsole
        return False

def save_data(username, data_dict):
    """Speichert lokal UND triggert den Cloud-Sync."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    json_data = json.dumps(data_dict)
    c.execute("INSERT OR REPLACE INTO user_storage (username, data) VALUES (?, ?)", 
              (username, json_data))
    conn.commit()
    conn.close()
    
    # AUTOMATISCHER SYNC
    sync_to_switchdrive()

def save_user_credentials(username, name, hashed_password):
    """Speichert neue User lokal UND triggert den Cloud-Sync."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO credentials (username, name, password) VALUES (?, ?, ?)", 
              (username, name, hashed_password))
    conn.commit()
    conn.close()
    
    # AUTOMATISCHER SYNC (damit der neue User sofort im Backup ist)
    sync_to_switchdrive()

# Die anderen Funktionen (init_db, load_data, load_all_credentials) 
# bleiben gleich wie vorher...
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_storage (username TEXT PRIMARY KEY, data TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS credentials (username TEXT PRIMARY KEY, name TEXT, password TEXT)''')
    conn.commit()
    conn.close()

def load_data(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT data FROM user_storage WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else {}

def load_all_credentials():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, name, password FROM credentials")
    rows = c.fetchall()
    conn.close()
    creds = {'usernames': {}}
    for row in rows:
        creds['usernames'][row[0]] = {'name': row[1], 'password': row[2]}
    return creds