import streamlit as st

st.title("📋 Übersicht")
user_data = st.session_state.current_notes

if not user_data:
    st.info("Noch keine Daten vorhanden.")
else:
    for n, i in user_data.items():
        w = sum(e['weight'] for e in i['exams'])
        st.write(f"### {n} ({i['credits']} ECTS)")
        st.progress(w/100)
        if w > 0:
            avg = sum(e['grade'] * e['weight'] for e in i['exams']) / w
            st.write(f"Aktueller Schnitt: **{avg:.2f}** (bei {w}%)")
        st.divider()