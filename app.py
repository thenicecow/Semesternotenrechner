import streamlit as st
import streamlit_authenticator as stauth
from database import init_db, load_data, save_data

# DB Initialisierung
init_db()

# Konfiguration der Benutzer (Passwörter hier im Klartext für das Beispiel)
# In Produktion sollten diese gehasht sein!
credentials = {
    'usernames': {
        'max123': {'name': 'Max Muster', 'password': '123'},
        'anna456': {'name': 'Anna Beispiel', 'password': '456'}
    }
}

authenticator = stauth.Authenticate(
    credentials,
    'notenrechner_cookie',
    'abcdef',
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    st.sidebar.title(f"Willkommen, {name}!")
    authenticator.logout('Logout', 'sidebar')

    # Username im Session State für Zugriff in Views speichern
    st.session_state["username"] = username

    # Daten des Users laden
    if 'current_notes' not in st.session_state:
        st.session_state.current_notes = load_data(username)

    # Navigation
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

    pg = st.navigation(pages)
    st.set_page_config(page_title="Notenrechner", layout="wide")
    pg.run()

elif authentication_status == False:
    st.error('Username/Passwort falsch')
elif authentication_status == None:
    st.info('Bitte einloggen')