import sqlite3
import json
import streamlit as st
from webdav4.client import Client

DB_FILE = 'notenrechner.db'

# --- WebDAV Konfiguration mit webdav4 ---

def sync_to_switchdrive():
    """
    Lädt die lokale Datenbank-Datei als Backup in das Switch Drive hoch.
    Verwendet die korrekte webdav4-Methode 'upload_file'.
    """
    try:
        # Erstellt den Client mit den Daten aus st.secrets
        client = Client(
            base_url=st.secrets["webdav"]["hostname"],
            auth=(st.secrets["webdav"]["username"], st.secrets["webdav"]["password"])
        )
        
        # Prüfung, ob die Verbindung zum Server grundsätzlich steht
        if client.exists("/"):
            # webdav4 benötigt 'upload_file' für den Pfad-basierten Upload
            client.upload_file(
                local_path=DB_FILE, 
                to_path="notenrechner_backup.db", 
                overwrite=True
            )
            return True
        else:
            st.error("Verbindung ok, aber Hauptverzeichnis nicht gefunden.")
            return False
            
    except Exception as e:
        # Gibt den genauen Fehler aus, falls z.B. die URL oder das Passwort falsch ist
        st.error(f"Cloud-Sync Fehler: {str(e)}")
        return False

# --- Lokale Datenbank Operationen (SQLite) ---

def init_db():
    """Initialisiert die Tabellen in der lokalen SQLite-Datei."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_storage 
                 (username TEXT PRIMARY KEY, data TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS credentials 
                 (username TEXT PRIMARY KEY, name TEXT, password TEXT)''')
    conn.commit()
    conn.close()

def save_data(username, data_dict):
    """Speichert Notendaten lokal."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    json_data = json.dumps(data_dict)
    c.execute("INSERT OR REPLACE INTO user_storage (username, data) VALUES (?, ?)", 
              (username, json_data))
    conn.commit()
    conn.close()

def load_data(username):
    """Lädt Notendaten lokal."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT data FROM user_storage WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else {}

def save_user_credentials(username, name, hashed_password):
    """Speichert Login-Daten lokal."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO credentials (username, name, password) VALUES (?, ?, ?)", 
              (username, name, hashed_password))
    conn.commit()
    conn.close()

def load_all_credentials():
    """Lädt alle User für den Authenticator."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, name, password FROM credentials")
    rows = c.fetchall()
    conn.close()
    
    creds = {'usernames': {}}
    for row in rows:
        creds['usernames'][row[0]] = {'name': row[1], 'password': row[2]}
    return creds