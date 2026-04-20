import streamlit as st
if 'subjects' not in st.session_state:
    st.session_state.subjects = {} 
    # Struktur: {"Mathe": {"credits": 3, "exams": [{"grade": 5.5, "weight": 20}]}}

# Setup der Seiten-Navigation
pages = {
    "Dashboard": [
        st.Page("views/dashboard.py", title="Dashboard", icon="📊"),
    ],
    "Verwaltung": [
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