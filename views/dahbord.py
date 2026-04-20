import streamlit as st

st.title("📊 Semester-Dashboard")
user_data = st.session_state.current_notes

if not user_data:
    st.info("Willkommen! Erfasse zuerst deine Fächer in der Verwaltung.")
else:
    # Berechnungen für Kennzahlen
    total_creds = sum(info['credits'] for info in user_data.values())
    done_creds = sum(info['credits'] for info in user_data.values() if sum(e['weight'] for e in info['exams']) == 100)
    
    col_a, col_b = st.columns(2)
    col_a.metric("Anzahl Module", len(user_data))
    col_b.metric("Eingetragene Credits", f"{total_creds} ECTS")

    st.subheader("Deine Fächer")
    cols = st.columns(3)
    for i, (name, info) in enumerate(user_data.items()):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{name}**")
                w = sum(e['weight'] for e in info['exams'])
                st.progress(w/100)
                if w > 0:
                    avg = sum(e['grade'] * e['weight'] for e in info['exams']) / w
                    st.write(f"Schnitt: `{avg:.2f}`")
                st.caption(f"{info['credits']} ECTS | {w}% fertig")

    # SEMESTERAUSLASTUNG BEREICH
    st.divider()
    st.subheader("🚀 Semesterauslastung")
    if total_creds > 0:
        ratio = done_creds / total_creds
        st.write(f"Du hast **{done_creds}** von **{total_creds}** Credits dieses Semesters abgeschlossen.")
        st.progress(ratio)
        
        if ratio == 1.0:
            st.success("Hervorragend! Das Semester ist vollständig abgeschlossen!")
            st.balloons()
        elif ratio > 0:
            st.info(f"Dein aktueller Fortschritt im gesamten Semester liegt bei {ratio*100:.1f}%.")