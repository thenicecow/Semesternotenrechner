import streamlit as st

st.title("⚖️ Gesamtauswertung")
user_data = st.session_state.current_notes

total_pts = 0.0
total_creds = 0.0
summary = []

for name, info in user_data.items():
    total_w = sum(e['weight'] for e in info['exams'])
    if total_w == 100:
        final_g = sum(e['grade'] * (e['weight']/100) for e in info['exams'])
        total_pts += final_g * info['credits']
        total_creds += info['credits']
        summary.append({"Fach": name, "Note": round(final_g, 2), "ECTS": info['credits']})

if summary:
    st.table(summary)
    st.header(f"Schnitt: {(total_pts / total_creds):.3f}")
else:
    st.info("Noch keine Fächer mit 100% Gewichtung fertig.")