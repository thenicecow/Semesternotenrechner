import streamlit as st
import pandas as pd

st.title("⚖️ Gesamtauswertung")
user_data = st.session_state.current_notes
pts, creds, sum_list = 0.0, 0.0, []

for n, i in user_data.items():
    w = sum(e['weight'] for e in i['exams'])
    if w == 100:
        note = sum(e['grade'] * (e['weight']/100) for e in i['exams'])
        pts += note * i['credits']
        creds += i['credits']
        sum_list.append({"Fach": n, "Note": round(note, 2), "ECTS": i['credits']})

if sum_list:
    st.table(sum_list)
    st.header(f"Schnitt: {(pts/creds):.3f}")
    csv = pd.DataFrame(sum_list).to_csv(index=False).encode('utf-8')
    st.download_button("CSV Export für Switch Drive", csv, "noten.csv", "text/csv")
else:
    st.warning("Keine fertigen Fächer (100%).")