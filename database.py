import sqlite3
import json
import streamlit as st
from webdav4.client import Client

DB_FILE = 'notenrechner.db'

# --- WebDAV Konfiguration mit webdav4 ---

def sync_to_switchdrive():
    """
    Lädt die lokale Datenbank-Datei als Backup in das Switch Drive hoch.
    Nutzt die webdav4 Bibliothek.
    """
    try:
        # Zugangsdaten aus st.secrets laden
        # WICHTIG: Hostname muss https://drive.switch.ch/remote.php/dav/files/DEINE_EMAIL/ sein
        client = Client(
            base_url=st.secrets["webdav"]["hostname"],
            auth=(st.secrets["webdav"]["username"], st.secrets["webdav"]["password"])
        )
        
        # Lokale Datei 'notenrechner.db' öffnen und hochladen
        with open(DB_FILE, 'rb') as f:
            # Überträgt die Datei in dein Hauptverzeichnis auf Switch Drive
            client.upload(content=f, to_path="notenrechner_backup.db", overwrite=True)
        
        return True
    except Exception as e:
        st.error(f"Cloud-Sync Fehler (webdav4): {str(e)}")
        return False

# --- Lokale Datenbank Operationen (SQLite) ---

def init_db():
    """Initialisiert die Tabellen für Benutzer und Notendaten."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Tabelle für die Notendaten der Fächer
    c.execute('''CREATE TABLE IF NOT EXISTS user_storage 
                 (username TEXT PRIMARY KEY, data TEXT)''')
    # Tabelle für die Login-Daten
    c.execute('''CREATE TABLE IF NOT EXISTS credentials 
                 (username TEXT PRIMARY KEY, name TEXT, password TEXT)''')
    conn.commit()
    conn.close()

def save_data(username, data_dict):
    """Speichert das Noten-Dictionary eines Users lokal."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    json_data = json.dumps(data_dict)
    c.execute("INSERT OR REPLACE INTO user_storage (username, data) VALUES (?, ?)", 
              (username, json_data))
    conn.commit()
    conn.close()

def load_data(username):
    """Lädt die lokalen Notendaten eines Users."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT data FROM user_storage WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else {}

def save_user_credentials(username, name, hashed_password):
    """Speichert ein neu registriertes Benutzerkonto lokal ab."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO credentials (username, name, password) VALUES (?, ?, ?)", 
              (username, name, hashed_password))
    conn.commit()
    conn.close()

def load_all_credentials():
    """Lädt alle registrierten Benutzer beim App-Start."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, name, password FROM credentials")
    rows = c.fetchall()
    conn.close()
    
    creds = {'usernames': {}}
    for row in rows:
        creds['usernames'][row[0]] = {'name': row[1], 'password': row[2]}
    return creds