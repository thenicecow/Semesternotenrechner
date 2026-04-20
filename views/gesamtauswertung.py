import streamlit as st
import pandas as pd

st.title("⚖️ Abschluss-Rechnung")
user_data = st.session_state.current_notes
total_pts, total_creds, final_list = 0.0, 0.0, []

for n, i in user_data.items():
    weight_sum = sum(e['weight'] for e in i['exams'])
    if weight_sum == 100:
        m_grade = sum(e['grade'] * (e['weight']/100) for e in i['exams'])
        total_pts += m_grade * i['credits']
        total_creds += i['credits']
        final_list.append({"Modul": n, "Abschlussnote": round(m_grade, 2), "ECTS": i['credits']})

if final_list:
    st.table(final_list)
    final_avg = total_pts / total_creds
    st.header(f"Gesamtdurchschnitt: {final_avg:.3f}")
    
    csv = pd.DataFrame(final_list).to_csv(index=False).encode('utf-8')
    st.download_button("📥 Noten als CSV für Switch Drive exportieren", csv, "noten_export.csv", "text/csv")
else:
    st.warning("Keine Module zu 100% abgeschlossen. Der Schnitt wird erst berechnet, wenn die volle Gewichtung erreicht ist.")