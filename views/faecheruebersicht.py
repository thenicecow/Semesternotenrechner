import streamlit as st

st.title("📋 Fächerübersicht")

user_data = st.session_state.current_notes

if not user_data:
    st.info("Noch keine Daten verfügbar.")
else:
    for name, info in user_data.items():
        exams = info['exams']
        total_w = sum(e['weight'] for e in exams)
        
        if total_w > 0:
            current_avg = sum(e['grade'] * e['weight'] for e in exams) / total_w
            st.subheader(f"{name} ({info['credits']} Credits)")
            st.write(f"Status: **{total_w}%** | Aktueller Schnitt: **{current_avg:.2f}**")
            st.progress(total_w / 100)
        else:
            st.write(f"**{name}**: Noch keine Noten eingetragen.")