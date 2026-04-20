import streamlit as st

st.title("Gesamtauswertung")

total_weighted_points = 0
total_credits = 0

for name, data in st.session_state.subjects.items():
    exams = data["exams"]
    if exams:
        # Berechne Modulnote
        total_weight = sum(e["weight"] for e in exams)
        if total_weight > 0:
            module_grade = sum(e["grade"] * e["weight"] for e in exams) / total_weight
            
            # Nur wenn das Modul abgeschlossen ist (100%), zählt es für den Schnitt
            if total_weight == 100:
                total_weighted_points += module_grade * data["credits"]
                total_credits += data["credits"]
                st.write(f"{name}: Note {module_grade:.2f} ({data['credits']} Credits)")
            else:
                st.write(f"{name}: Noch offen ({total_weight}% erfasst)")

if total_credits > 0:
    final_avg = total_weighted_points / total_credits
    st.header(f"Gesamtdurchschnitt: {final_avg:.2f}")