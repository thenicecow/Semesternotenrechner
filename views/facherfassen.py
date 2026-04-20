import streamlit as st
from database import save_data

st.title("➕ Fächer erfassen")
user_data = st.session_state.current_notes

with st.form("subject_form", clear_on_submit=True):
    name = st.text_input("Name des Fachs")
    credits = st.number_input("Credits", min_value=1.0, value=3.0, step=0.5)
    submit = st.form_submit_button("Fach speichern")

if submit and name:
    user_data[name] = {"credits": credits, "exams": []}
    save_data(st.session_state["username"], user_data)
    st.success(f"'{name}' gespeichert!")
    st.rerun()

st.write("### Deine Fächer")
for subj in list(user_data.keys()):
    col1, col2 = st.columns([3, 1])
    col1.write(f"**{subj}** ({user_data[subj]['credits']} Credits)")
    if col2.button("Löschen", key=f"del_{subj}"):
        del user_data[subj]
        save_data(st.session_state["username"], user_data)
        st.rerun()