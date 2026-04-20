import sqlite3
import json
import streamlit as st
from webdav4.client import Client

DB_FILE = 'notenrechner.db'

# --- WebDAV Konfiguration mit webdav4 ---

def sync_to_switchdrive():
    """
    Lädt die lokale Datenbank-Datei als Backup in das Switch Drive hoch.
    Stelle sicher, dass 'webdav4' in deiner requirements.txt steht.
    """
    try:
        # Erstellt den Client mit den Daten aus secrets.toml
        # WICHTIG: Hostname muss https://drive.switch.ch/remote.php/dav/files/DEINE_EMAIL/ sein
        client = Client(
            base_url=st.secrets["webdav"]["hostname"],
            auth=(st.secrets["webdav"]["username"], st.secrets["webdav"]["password"])
        )
        
        # Testet, ob die Verbindung zum Root-Verzeichnis funktioniert
        if client.exists("/"):
            with open(DB_FILE, 'rb') as f:
                # Überträgt die Datei und überschreibt eine alte Version falls vorhanden
                # Die Datei erscheint in deinem Switch Drive als 'notenrechner_backup.db'
                client.upload(content=f, to_path="/notenrechner_backup.db", overwrite=True)
            return True
        else:
            st.error("Verbindung zu Switch Drive möglich, aber Verzeichnis nicht erreichbar.")
            return False
            
    except Exception as e:
        # Gibt die genaue Fehlermeldung in der App aus (hilfreich bei 401 oder 404 Fehlern)
        st.error(f"Cloud-Sync Fehler: {str(e)}")
        return False

# --- Lokale Datenbank Operationen (SQLite) ---

def init_db():
    """Initialisiert die lokalen Tabellen auf dem Cloud-Server."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Tabelle für die Fächer und Noten
    c.execute('''CREATE TABLE IF NOT EXISTS user_storage 
                 (username TEXT PRIMARY KEY, data TEXT)''')
    # Tabelle für die Benutzer-Accounts
    c.execute('''CREATE TABLE IF NOT EXISTS credentials 
                 (username TEXT PRIMARY KEY, name TEXT, password TEXT)''')
    conn.commit()
    conn.close()

def save_data(username, data_dict):
    """Speichert das Noten-Dictionary eines Users lokal in der SQLite-DB."""
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
    """Speichert ein neues Benutzerkonto nach der Registrierung lokal ab."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO credentials (username, name, password) VALUES (?, ?, ?)", 
              (username, name, hashed_password))
    conn.commit()
    conn.close()

def load_all_credentials():
    """Lädt alle registrierten Benutzer für den Authenticator beim App-Start."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, name, password FROM credentials")
    rows = c.fetchall()
    conn.close()
    
    creds = {'usernames': {}}
    for row in rows:
        creds['usernames'][row[0]] = {'name': row[1], 'password': row[2]}
    return creds