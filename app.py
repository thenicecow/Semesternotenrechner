import streamlit as st
import streamlit_authenticator as stauth
from database import init_db, load_data, save_data, save_user_credentials, load_all_credentials, sync_to_switchdrive

# Seite konfigurieren
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
            # FIX: pre_authorization=False hinzugefügt, damit der Fehler verschwindet
            res = authenticator.register_user(location='main', pre_authorization=False)
            
            if res and res[1]: # Wenn ein Username zurückgegeben wurde
                new_username = res[1]
                new_user_data = st.session_state.credentials['usernames'][new_username]
                
                # In der lokalen Datenbank speichern
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

# Wenn eingeloggt
if st.session_state.get("authentication_status"):
    username = st.session_state['username']
    st.sidebar.title(f"👋 Hallo {st.session_state['name']}")
    
    authenticator.logout('Logout', 'sidebar')

    # Cloud Sync Button
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
    
    pg = st.navigation(pages)
    pg.run()
    
    # Automatisch lokal speichern
    save_data(username, st.session_state.current_notes)

elif st.session_state.get("authentication_status") is False:
    st.error('Username/Passwort ist falsch.')