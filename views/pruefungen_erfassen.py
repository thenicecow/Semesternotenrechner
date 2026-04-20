import streamlit as st
import pandas as pd
from database import save_data

st.title("📝 Prüfungsnoten")
user_data = st.session_state.current_notes

if user_data:
    sel = st.selectbox("Modul wählen", list(user_data.keys()))
    with st.form("add_exam", clear_on_submit=True):
        g = st.number_input("Note", 1.0, 6.0, 5.0, 0.01)
        w = st.number_input("Gewichtung (%)", 1, 100, 20)
        if st.form_submit_button("Note speichern"):
            user_data[sel]['exams'].append({"grade": g, "weight": w})
            save_data(st.session_state["username"], user_data)
            st.rerun()
    
    if user_data[sel]['exams']:
        st.dataframe(pd.DataFrame(user_data[sel]['exams']), use_container_width=True)
        if st.button("Alle Prüfungen in diesem Modul löschen"):
            user_data[sel]['exams'] = []
            save_data(st.session_state["username"], user_data)
            st.rerun()