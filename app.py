import streamlit as st
import streamlit_authenticator as stauth
from database import init_db, load_data, save_data, save_user_credentials, load_all_credentials

st.set_page_config(page_title="Mein Notenrechner", layout="wide")
init_db()

if 'credentials' not in st.session_state:
    st.session_state.credentials = load_all_credentials()

authenticator = stauth.Authenticate(
    st.session_state.credentials,
    'notenrechner_cookie',
    'abcdef',
    cookie_expiry_days=30
)

# LOGIN / REGISTRIERUNG
if not st.session_state.get("authentication_status"):
    tab1, tab2 = st.tabs(["Anmelden", "Registrieren"])
    with tab2:
        res = authenticator.register_user(location='main', preauthorization=False)
        if res and res[1]:
            new_username = res[1]
            new_user_data = st.session_state.credentials['usernames'][new_username]
            save_user_credentials(new_username, new_user_data['name'], new_user_data['password'])
            st.success('Registriert! Cloud-Backup wurde aktualisiert.')
    with tab1:
        authenticator.login(location='main')

# APP INHALT
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
    
    # AUTOMATISCHE SPEICHERUNG & SYNC
    # Dies wird bei jeder Interaktion (z.B. Note eingeben) ausgeführt
    save_data(username, st.session_state.current_notes)

elif st.session_state.get("authentication_status") is False:
    st.error('Login falsch.')