import streamlit as st
import streamlit_authenticator as stauth
from database import init_db, load_data, save_data

# 1. Datenbank beim Start initialisieren
init_db()

# 2. Benutzer-Konfiguration
# WICHTIG: Ersetze diese durch deine gewünschten Logins
credentials = {
    'usernames': {
        'max123': {'name': 'Max Muster', 'password': '123'},
        'anna456': {'name': 'Anna Beispiel', 'password': '456'}
    }
}

# 3. Authenticator Objekt erstellen
authenticator = stauth.Authenticate(
    credentials,
    'notenrechner_cookie',
    'abcdef',
    cookie_expiry_days=30
)

# 4. Login-Prozess (KORRIGIERTE VERSION)
# Falls 'location' Fehler wirft, nutzt das Paket hier die korrekten Standardwerte
try:
    # Neue Syntax für Version 0.3.x+
    # Wir übergeben keine festen Strings mehr ohne Namen, um den ValueError zu vermeiden
    result = authenticator.login(location='main')
    
    # Je nach Version gibt login() unterschiedliche Dinge zurück, 
    # wir holen uns den Status direkt aus dem Authenticator-Objekt
    authentication_status = st.session_state.get("authentication_status")
    username = st.session_state.get("username")
    name = st.session_state.get("name")
except Exception as e:
    st.error(f"Fehler beim Login-Modul: {e}")
    authentication_status = None

# 5. Logik basierend auf dem Login-Status
if authentication_status:
    # Sidebar Setup
    st.sidebar.title(f"👋 Hallo {st.session_state['name']}")
    authenticator.logout('Logout', 'sidebar')

    # Daten des spezifischen Users aus der Datenbank laden
    if 'current_notes' not in st.session_state:
        st.session_state.current_notes = load_data(st.session_state['username'])

    # Navigation definieren (Pfade zu deinen Dateien in /views)
    pages = {
        "Übersicht": [
            st.Page("views/dahbord.py", title="Dashboard", icon="📊"),
        ],
        "Eingabe": [
            st.Page("views/facherfassen.py", title="Fächer erfassen", icon="➕"),
            st.Page("views/pruefungen_erfassen.py", title="Prüfungen erfassen", icon="📝"),
        ],
        "Auswertung": [
            st.Page("views/faecheruebersicht.py", title="Fächerübersicht", icon="📋"),
            st.Page("views/gesamtauswertung.py", title="Gesamtauswertung", icon="⚖️"),
        ]
    }

    # Navigation ausführen
    pg = st.navigation(pages)
    
    # Page Config muss hier stehen, falls sie nicht schon global gesetzt wurde
    # st.set_page_config(page_title="Notenrechner", layout="wide") 
    
    pg.run()

elif authentication_status == False:
    st.error('Username oder Passwort ist falsch.')
    
elif authentication_status == None:
    st.info('Willkommen! Bitte logge dich ein, um deine Noten zu verwalten.')
    st.caption("Hinweis: Falls du noch keinen Account hast, kontaktiere den Admin.")

# Falls du ein automatisches Speichern am Ende jeder Seite willst:
if authentication_status and 'current_notes' in st.session_state:
    save_data(st.session_state['username'], st.session_state.current_notes)