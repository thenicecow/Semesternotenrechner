import sqlite3
import json
import streamlit as st
from webdav4.client import Client
import tempfile
import os
import datetime

DB_FILE = 'notenrechner.db'


def sync_to_switchdrive():
    """Lädt die gesamte Datenbank als Backup im Hintergrund hoch (optional)."""
    try:
        client = Client(
            base_url=st.secrets["webdav"]["hostname"],
            auth=(st.secrets["webdav"]["username"], st.secrets["webdav"]["password"])
        )
        client.upload_file(local_path=DB_FILE, to_path="notenrechner_backup.db", overwrite=True)
        return True
    except Exception as e:
        print(f"Automatischer Sync fehlgeschlagen: {e}")
        return False


def save_data(username, data_dict):
    """Speichert die Noten lokal und sendet sie per-user an SwitchDrive hoch."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    json_data = json.dumps(data_dict)
    c.execute("INSERT OR REPLACE INTO user_storage (username, data) VALUES (?, ?)", (username, json_data))
    conn.commit()
    conn.close()

    # Per-user Upload (fehlerdämpfend)
    try:
        sync_upload_user(username, data_dict)
    except Exception as e:
        print(f"User upload fehlgeschlagen: {e}")


def save_user_credentials(username, name, hashed_password):
    """Speichert neue Benutzer und sichert die DB sofort in der Cloud (Backup)."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO credentials (username, name, password) VALUES (?, ?, ?)", (username, name, hashed_password))
    conn.commit()
    conn.close()

    # Optional: Backup der gesamten DB
    try:
        sync_to_switchdrive()
    except Exception:
        pass


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


def _get_webdav_client():
    """Erstellt einen WebDAV-Client oder wirft Exception, wenn Secrets fehlen."""
    try:
        client = Client(
            base_url=st.secrets["webdav"]["hostname"],
            auth=(st.secrets["webdav"]["username"], st.secrets["webdav"]["password"])
        )
        return client
    except Exception as e:
        raise RuntimeError(f"WebDAV Client konnte nicht erstellt werden: {e}")


def _remote_user_path(username):
    # Speicherung pro Nutzer in einem Ordner 'userdata'
    return f"userdata/{username}.json"


def sync_upload_user(username, data_dict):
    """Lädt die Benutzerdaten als JSON auf SwitchDrive hoch (fehlertolerant)."""
    client = _get_webdav_client()
    remote_path = _remote_user_path(username)

    fd, tmp_path = tempfile.mkstemp(suffix='.json')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False)

        # Hauptdatei pro Benutzer (gleichbleibender Pfad)
        client.upload_file(local_path=tmp_path, to_path=remote_path, overwrite=True)

        # Zusätzlich: zeitgestempeltes Backup pro Benutzer anlegen
        ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        backup_remote = f"userdata/backups/{username}_backup_{ts}.json"
        try:
            client.upload_file(local_path=tmp_path, to_path=backup_remote, overwrite=False)
        except Exception:
            # Backup fehlschlagen lassen wir stillschweigend, Hauptupload ist wichtiger
            pass

        return True
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def sync_download_user(username):
    """Lädt die Benutzerdaten von SwitchDrive herunter und gibt sie als dict zurück.
    Gibt None zurück, wenn keine Remote-Datei existiert oder bei Fehlern.
    """
    try:
        client = _get_webdav_client()
    except Exception as e:
        print(f"WebDAV nicht konfiguriert: {e}")
        return None

    remote_path = _remote_user_path(username)
    fd, tmp_path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    try:
        try:
            client.download_file(remote_path, to_path=tmp_path)
        except Exception as e:
            print(f"Remote-Datei nicht gefunden oder Download-Fehler: {e}")
            try:
                os.remove(tmp_path)
            except Exception:
                pass
            return None

        with open(tmp_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass