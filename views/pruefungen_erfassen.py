import streamlit as st

st.title("Prüfungsnoten eingeben")
if not st.session_state.subjects:
    st.warning("Bitte erstelle zuerst ein Fach unter 'Fächer erfassen'.")
else:
    subject = st.selectbox("Fach auswählen", options=list(st.session_state.subjects.keys()))
    
    with st.form("add_exam"):
        grade = st.number_input("Note", min_value=1.0, max_value=6.0, step=0.25)
        weight = st.number_input("Gewichtung in %", min_value=1, max_value=100)
        if st.form_submit_button("Note hinzufügen"):
            st.session_state.subjects[subject]["exams"].append({"grade": grade, "weight": weight})
            st.success("Note gespeichert!")