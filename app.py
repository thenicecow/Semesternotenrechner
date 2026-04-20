import streamlit as st
import streamlit_authenticator as stauth
from database import init_db, load_data, save_data
import yaml

# 1. Datenbank beim Start initialisieren
init_db()

# 2. Session State für Benutzer-Konfiguration
# Wir laden die User-Liste (hier beispielhaft, idealerweise käme diese auch aus einer DB)
if 'credentials' not in st.session_state:
    st.session_state.credentials = {
        'usernames': {
            'admin': {'name': 'Admin', 'password': '123'} # Standard-User
        }
    }

# 3. Authenticator Objekt erstellen
authenticator = stauth.Authenticate(
    st.session_state.credentials,
    'notenrechner_cookie',
    'abcdef',
    cookie_expiry_days=30
)

# --- REGISTRIERUNG ODER LOGIN ---
# Wir nutzen Tabs, damit der User wählen kann
tab1, tab2 = st.tabs(["Anmelden", "Registrieren"])

with tab2:
    try:
        # Das Register-Widget
        email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(location='main')
        if email_of_registered_user:
            st.success('Benutzer erfolgreich registriert! Du kannst dich jetzt anmelden.')
            # Hier könnte man die neuen Credentials dauerhaft speichern
    except Exception as e:
        st.error(e)

with tab1:
    try:
        authenticator.login(location='main')
    except Exception as e:
        st.error(f"Fehler beim Login: {e}")

# --- LOGIK BASIEREND AUF LOGIN ---
authentication_status = st.session_state.get("authentication_status")

if authentication_status:
    # Sidebar Setup
    st.sidebar.title(f"👋 Hallo {st.session_state['name']}")
    authenticator.logout('Logout', 'sidebar')

    # Daten des spezifischen Users laden
    username = st.session_state['username']
    if 'current_notes' not in st.session_state:
        st.session_state.current_notes = load_data(username)

    # Navigation definieren
    pages = {
        "Übersicht": [st.Page("views/dahbord.py", title="Dashboard", icon="📊")],
        "Eingabe": [
            st.Page("views/facherfassen.py", title="Fächer erfassen", icon="➕"),
            st.Page("views/pruefungen_erfassen.py", title="Prüfungen erfassen", icon="📝"),
        ],
        "Auswertung": [
            st.Page("views/faecheruebersicht.py", title="Fächerübersicht", icon="📋"),
            st.Page("views/gesamtauswertung.py", title="Gesamtauswertung", icon="⚖️"),
        ]
    }

    pg = st.navigation(pages)
    pg.run()

    # Automatisches Speichern der Noten
    save_data(username, st.session_state.current_notes)

elif authentication_status == False:
    st.error('Username oder Passwort ist falsch.')
elif authentication_status == None:
    st.info('Bitte logge dich ein oder erstelle ein Konto.')