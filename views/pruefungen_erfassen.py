import streamlit as st
import pandas as pd
from database import save_data

st.title("📝 Prüfungen erfassen")
user_data = st.session_state.current_notes

if not user_data:
    st.warning("Erstelle erst ein Fach.")
else:
    selected = st.selectbox("Fach wählen", list(user_data.keys()))
    
    with st.form("exam_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        grade = col1.number_input("Note", 1.0, 6.0, 5.0, 0.05)
        weight = col2.number_input("Gewicht %", 1, 100, 10)
        if st.form_submit_button("Hinzufügen"):
            user_data[selected]['exams'].append({"grade": grade, "weight": weight})
            save_data(st.session_state["username"], user_data)
            st.success("Note gespeichert!")
            st.rerun()

    if user_data[selected]['exams']:
        st.table(pd.DataFrame(user_data[selected]['exams']))
        if st.button("Fach leeren"):
            user_data[selected]['exams'] = []
            save_data(st.session_state["username"], user_data)
            st.rerun()