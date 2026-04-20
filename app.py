import streamlit as st
import streamlit_authenticator as stauth
from database import init_db, load_data, save_data, save_user_credentials, load_all_credentials, sync_to_switchdrive

# Seite konfigurieren (Muss als allererstes stehen)
st.set_page_config(page_title="Mein Notenrechner", layout="wide")

# Datenbank initialisieren
init_db()

# Benutzerdaten laden
if 'credentials' not in st.session_state:
    st.session_state.credentials = load_all_credentials()

# Authenticator Setup
authenticator = stauth.Authenticate(
    st.session_state.credentials,
    'notenrechner_cookie',
    'abcdef',
    cookie_expiry_days=30
)

# Login / Registrierung Bereich
if not st.session_state.get("authentication_status"):
    tab1, tab2 = st.tabs(["Anmelden", "Registrieren"])
    
    with tab2:
        try:
            res = authenticator.register_user(location='main')
            if res[1]: # Wenn Username zurückgegeben wurde
                new_user = st.session_state.credentials['usernames'][res[1]]
                save_user_credentials(res[1], new_user['name'], new_user['password'])
                st.success('Registrierung erfolgreich! Du kannst dich jetzt anmelden.')
        except Exception as e:
            st.error(f"Fehler bei Registrierung: {e}")

    with tab1:
        try:
            authenticator.login(location='main')
        except Exception as e:
            st.error(f"Login Fehler: {e}")

# Wenn eingeloggt
if st.session_state.get("authentication_status"):
    username = st.session_state['username']
    st.sidebar.title(f"👋 Hallo {st.session_state['name']}")
    
    # Logout Button
    authenticator.logout('Logout', 'sidebar')

    # Cloud Sync Button in der Sidebar
    st.sidebar.divider()
    if st.sidebar.button("🔄 Cloud-Sync (Switch Drive)"):
        with st.sidebar.spinner("Synchronisiere..."):
            if sync_to_switchdrive():
                st.sidebar.success("In Switch Drive gesichert!")

    # Noten laden
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
    
    # App ausführen
    pg = st.navigation(pages)
    pg.run()
    
    # Automatisch lokal speichern nach jeder Interaktion
    save_data(username, st.session_state.current_notes)

elif st.session_state.get("authentication_status") is False:
    st.error('Username/Passwort ist falsch.')