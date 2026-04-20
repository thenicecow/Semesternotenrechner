import streamlit as st
import streamlit_authenticator as stauth
from database import init_db, load_data, save_data, save_user_credentials, load_all_credentials, sync_to_switchdrive

# 1. Seite konfigurieren (Muss die erste Streamlit-Anweisung sein)
st.set_page_config(page_title="Mein Notenrechner", layout="wide")

# 2. Datenbank initialisieren
init_db()

# 3. Benutzerdaten aus der lokalen Datenbank laden
if 'credentials' not in st.session_state:
    st.session_state.credentials = load_all_credentials()

# 4. Authenticator Setup
authenticator = stauth.Authenticate(
    st.session_state.credentials,
    'notenrechner_cookie',
    'abcdef',
    cookie_expiry_days=30
)

# --- LOGIN / REGISTRIERUNG BEREICH ---
if not st.session_state.get("authentication_status"):
    tab1, tab2 = st.tabs(["Anmelden", "Registrieren"])
    
    with tab2:
        try:
            # FIX: 'preauthorization' ohne Unterstrich geschrieben
            res = authenticator.register_user(location='main', preauthorization=False)
            
            if res and res[1]: 
                new_username = res[1]
                new_user_data = st.session_state.credentials['usernames'][new_username]
                
                # Neuen User permanent in der lokalen DB speichern
                save_user_credentials(
                    new_username, 
                    new_user_data['name'], 
                    new_user_data['password']
                )
                st.success('Registrierung erfolgreich! Bitte wechsle zum Tab "Anmelden".')
        except Exception as e:
            st.error(f"Fehler bei Registrierung: {e}")

    with tab1:
        try:
            authenticator.login(location='main')
        except Exception as e:
            st.error(f"Login Fehler: {e}")

# --- APP INHALT (WENN EINGELOGGT) ---
if st.session_state.get("authentication_status"):
    username = st.session_state['username']
    st.sidebar.title(f"👋 Hallo {st.session_state['name']}")
    
    # Logout Button in der Sidebar
    authenticator.logout('Logout', 'sidebar')

    # Cloud Sync Button in der Sidebar
    st.sidebar.divider()
    st.sidebar.subheader("Datensicherung")
    if st.sidebar.button("🔄 Cloud-Sync (Switch Drive)"):
        with st.sidebar.spinner("Synchronisiere mit Switch Drive..."):
            if sync_to_switchdrive():
                st.sidebar.success("In Switch Drive gesichert!")
            else:
                # Fehler wird bereits in sync_to_switchdrive via st.error ausgegeben
                pass

    # Notendaten für den aktuellen User laden
    if 'current_notes' not in st.session_state:
        st.session_state.current_notes = load_data(username)

    # Navigation definieren
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
    pg.run()
    
    # Nach jeder Aktion: Noten lokal speichern
    save_data(username, st.session_state.current_notes)

elif st.session_state.get("authentication_status") is False:
    st.error('Username oder Passwort ist falsch.')

elif st.session_state.get("authentication_status") is None:
    st.info('Willkommen! Bitte logge dich ein oder erstelle ein neues Konto.')