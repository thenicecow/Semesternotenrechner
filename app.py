import streamlit as st
import streamlit_authenticator as stauth
from database import init_db, load_data, save_data, save_user_credentials, load_all_credentials

# 1. Seite konfigurieren
st.set_page_config(page_title="Mein Notenrechner", layout="wide")

# 2. Datenbank initialisieren
init_db()

# 3. Credentials laden
if 'credentials' not in st.session_state:
    st.session_state.credentials = load_all_credentials()

# 4. Authenticator Setup
authenticator = stauth.Authenticate(
    st.session_state.credentials,
    'notenrechner_cookie',
    'abcdef',
    cookie_expiry_days=30
)

# --- AUTHENTIFIZIERUNGSLOGIK ---

# Falls noch nicht eingeloggt
if not st.session_state.get("authentication_status"):
    
    # State für die Ansicht steuern (Default: Login)
    if "view" not in st.session_state:
        st.session_state.view = "login"

    # A) REINE REGISTRIERUNGS-ANSICHT
    if st.session_state.view == "register":
        st.title("Neues Konto erstellen")
        try:
            res = authenticator.register_user(location='main', preauthorization=False)
            if res and res[1]:
                new_username = res[1]
                new_user_data = st.session_state.credentials['usernames'][new_username]
                save_user_credentials(new_username, new_user_data['name'], new_user_data['password'])
                st.success('Registrierung erfolgreich!')
                if st.button("Zurück zum Login"):
                    st.session_state.view = "login"
                    st.rerun()
        except Exception as e:
            st.error(f"Fehler: {e}")
        
        if st.button("Abbrechen"):
            st.session_state.view = "login"
            st.rerun()

    # B) REINE LOGIN-ANSICHT
    else:
        st.title("Willkommen beim Notenrechner")
        try:
            authenticator.login(location='main')
        except Exception as e:
            st.error(f"Login Fehler: {e}")
            
        st.write("---")
        if st.button("Noch kein Konto? Hier registrieren"):
            st.session_state.view = "register"
            st.rerun()

# --- HAUPTAPP (EINGELOGGT) ---
if st.session_state.get("authentication_status"):
    username = st.session_state['username']
    st.sidebar.title(f"👋 Hallo {st.session_state['name']}")
    authenticator.logout('Logout', 'sidebar')

    if 'current_notes' not in st.session_state:
        st.session_state.current_notes = load_data(username)

    # Navigation
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
    
    # Automatischer Speicher- & Cloud-Sync (via database.py)
    save_data(username, st.session_state.current_notes)

elif st.session_state.get("authentication_status") is False:
    st.error('Username oder Passwort ist falsch.')
    if st.button("Erneut versuchen"):
        st.rerun()