import streamlit as st
from database import save_data

st.title("➕ Module verwalten")
user_data = st.session_state.current_notes

with st.form("add_subject", clear_on_submit=True):
    name = st.text_input("Name des Moduls")
    creds = st.number_input("Credits (ECTS)", 0.5, 30.0, 3.0, 0.5)
    if st.form_submit_button("Hinzufügen"):
        if name:
            user_data[name] = {"credits": creds, "exams": []}
            save_data(st.session_state["username"], user_data)
            st.rerun()

st.write("### Liste deiner Module")
for s in list(user_data.keys()):
    c1, c2 = st.columns([5, 1])
    c1.write(f"**{s}** ({user_data[s]['credits']} ECTS)")
    if c2.button("🗑️", key=f"del_{s}"):
        del user_data[s]
        save_data(st.session_state["username"], user_data)
        st.rerun()