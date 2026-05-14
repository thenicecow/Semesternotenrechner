import streamlit as st
import streamlit_authenticator as stauth
from database import init_db, load_data, save_data, save_user_credentials, load_all_credentials, sync_download_user

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
            # register_user gibt (name, username, password) oder ähnliche Formen
            if res and len(res) >= 2 and res[1]:
                new_username = res[1]

                # Stelle sicher, dass die in-memory credentials die neue User-Entry hat
                # Streamlit-Authenticator trägt sie normalerweise in st.session_state.credentials ein.
                new_user_data = st.session_state.credentials.get('usernames', {}).get(new_username)
                if new_user_data:
                    # Persistiere in der lokalen DB (hashed password wird bereits erwartet)
                    save_user_credentials(new_username, new_user_data.get('name', ''), new_user_data.get('password', ''))

                # Aktualisiere die lokal gelesenen credentials, damit login sofort möglich ist
                st.session_state.credentials = load_all_credentials()

                st.success('Registrierung erfolgreich! Bitte melde dich nun an.')
                # Explizit auf Login-View zurücksetzen
                if st.button("Zum Login"):
                    st.session_state.view = "login"
                    # Setze authentication_status klar auf False, um Fehlzustände zu vermeiden
                    st.session_state['authentication_status'] = False
                    st.rerun()
        except Exception as e:
            st.error(f"Fehler bei der Registrierung: {e}")

        if st.button("Abbrechen"):
            st.session_state.view = "login"
            st.rerun()

    # B) REINE LOGIN-ANSICHT
    else:
        st.title("Willkommen beim Notenrechner")
        try:
            # Verwende die expliziten Rückgabewerte des Authenticators und
            # setze den session_state zuverlässig. Viele Fehler beim Login
            # entstehen, wenn die Rückgabewerte ignoriert werden.
            name, authentication_status, username = authenticator.login(location='main')

            # Nur setzen wenn nicht None (kompatibel mit verschiedenen Versionen)
            if name is not None:
                st.session_state['name'] = name
            if authentication_status is not None:
                st.session_state['authentication_status'] = authentication_status
            if username is not None:
                st.session_state['username'] = username

            # Bei erfolgreichem Login die Seite neu laden, damit der "eingeloggt"-Zweig
            # sofort ausgeführt wird.
            if st.session_state.get('authentication_status'):
                        # Nach erfolgreichem Login: versuche Remote-Daten herunterzuladen
                        try:
                            remote = sync_download_user(username)
                            if remote is not None:
                                # Überschreibe die lokalen current_notes mit den Remote-Daten
                                st.session_state['current_notes'] = remote
                        except Exception as e:
                            st.warning(f"Remote-Daten konnten nicht geladen werden: {e}")

                        st.experimental_rerun()

        except Exception as e:
            # Mehr Details im Fehlerfall, damit der Nutzer und Entwickler sehen, was schief lief
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