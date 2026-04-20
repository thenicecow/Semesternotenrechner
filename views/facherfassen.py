import streamlit as st

st.title("Fächer erfassen")
with st.form("add_subject"):
    name = st.text_input("Name des Fachs")
    credits = st.number_input("Credits", min_value=0.5, step=0.5)
    if st.form_submit_button("Speichern"):
        if name and name not in st.session_state.subjects:
            st.session_state.subjects[name] = {"credits": credits, "exams": []}
            st.success(f"{name} hinzugefügt!")