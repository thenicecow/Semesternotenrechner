import streamlit as st
import pandas as pd

st.set_page_config(page_title="Notenrechner Semester", layout="wide")

st.title("Notenrechner für Semester und Module")
st.markdown(
    """
    Diese App berechnet:
    1. die **Endnote pro Fach** aus mehreren Teilprüfungen mit Prozentanteilen
    2. den **credit-gewichteten Gesamtschnitt** über alle Fächer
    """
)

# Initialisierung des Session State
if "subjects" not in st.session_state:
    st.session_state.subjects = []


def calculate_subject_grade(exams):
    """Berechnet die Fachnote aus gewichteten Teilprüfungen."""
    total_weight = sum(exam["weight"] for exam in exams)
    if total_weight == 0:
        return None, total_weight

    weighted_grade = sum(exam["grade"] * (exam["weight"] / 100) for exam in exams)
    return weighted_grade, total_weight


def calculate_overall_grade(subjects):
    """Berechnet den credit-gewichteten Gesamtschnitt."""
    valid_subjects = [s for s in subjects if s.get("final_grade") is not None and s.get("credits", 0) > 0]
    total_credits = sum(subject["credits"] for subject in valid_subjects)

    if total_credits == 0:
        return None, 0

    weighted_sum = sum(subject["final_grade"] * subject["credits"] for subject in valid_subjects)
    overall = weighted_sum / total_credits
    return overall, total_credits


st.header("1. Fach hinzufügen")

with st.form("subject_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        subject_name = st.text_input("Fachname", placeholder="z. B. Mathematik")
    with col2:
        credits = st.number_input("Credits", min_value=0.0, step=0.5, value=3.0)

    st.subheader("Teilprüfungen / Leistungen")
    st.caption("Für jede Teilprüfung gibst du eine Note und den Prozentanteil ein.")

    num_exams = st.number_input("Anzahl Teilprüfungen", min_value=1, max_value=20, value=4, step=1)

    exams = []
    for i in range(int(num_exams)):
        st.markdown(f"**Teilprüfung {i + 1}**")
        c1, c2 = st.columns(2)
        with c1:
            exam_name = st.text_input(f"Bezeichnung {i + 1}", value=f"Prüfung {i + 1}")
            exam_grade = st.number_input(
                f"Note {i + 1}",
                min_value=1.0,
                max_value=6.0,
                value=4.0,
                step=0.1,
                format="%.1f",
            )
        with c2:
            exam_weight = st.number_input(
                f"Prozentanteil {i + 1}",
                min_value=0.0,
                max_value=100.0,
                value=25.0,
                step=1.0,
                format="%.1f",
            )

        exams.append(
            {
                "name": exam_name,
                "grade": float(exam_grade),
                "weight": float(exam_weight),
            }
        )

    submitted = st.form_submit_button("Fach speichern")

    if submitted:
        if not subject_name.strip():
            st.error("Bitte gib einen Fachnamen ein.")
        else:
            final_grade, total_weight = calculate_subject_grade(exams)

            subject = {
                "name": subject_name.strip(),
                "credits": float(credits),
                "exams": exams,
                "final_grade": final_grade,
                "total_weight": total_weight,
            }
            st.session_state.subjects.append(subject)
            st.success(f"Fach '{subject_name}' wurde gespeichert.")


st.header("2. Gespeicherte Fächer")

if not st.session_state.subjects:
    st.info("Noch keine Fächer erfasst.")
else:
    for idx, subject in enumerate(st.session_state.subjects):
        with st.expander(f"{subject['name']} ({subject['credits']} Credits)", expanded=False):
            exams_df = pd.DataFrame(subject["exams"])
            exams_df = exams_df.rename(
                columns={
                    "name": "Teilprüfung",
                    "grade": "Note",
                    "weight": "Prozentanteil",
                }
            )
            st.dataframe(exams_df, use_container_width=True)

            if abs(subject["total_weight"] - 100) > 1e-9:
                st.warning(
                    f"Die Prozentanteile ergeben {subject['total_weight']:.1f}% statt 100%. "
                    f"Die Fachnote wurde trotzdem mit den eingegebenen Prozenten berechnet."
                )
            else:
                st.success(f"Die Prozentanteile ergeben genau 100%.")

            if subject["final_grade"] is not None:
                st.metric("Berechnete Fachnote", f"{subject['final_grade']:.2f}")
                st.metric(
                    "Beitrag zum credit-gewichteten Schnitt",
                    f"{subject['final_grade'] * subject['credits']:.2f}",
                )

            if st.button("Fach löschen", key=f"delete_{idx}"):
                st.session_state.subjects.pop(idx)
                st.rerun()


st.header("3. Gesamtauswertung")

if st.session_state.subjects:
    summary_rows = []
    for subject in st.session_state.subjects:
        final_grade = subject["final_grade"]
        credits_value = subject["credits"]
        weighted_points = final_grade * credits_value if final_grade is not None else None

        summary_rows.append(
            {
                "Fach": subject["name"],
                "Fachnote": round(final_grade, 2) if final_grade is not None else None,
                "Credits": credits_value,
                "Note x Credits": round(weighted_points, 2) if weighted_points is not None else None,
                "Prozentsumme": round(subject["total_weight"], 1),
            }
        )

    summary_df = pd.DataFrame(summary_rows)
    st.dataframe(summary_df, use_container_width=True)

    overall_grade, total_credits = calculate_overall_grade(st.session_state.subjects)

    c1, c2 = st.columns(2)
    with c1:
        if overall_grade is not None:
            st.metric("Credit-gewichteter Gesamtschnitt", f"{overall_grade:.2f}")
        else:
            st.metric("Credit-gewichteter Gesamtschnitt", "-")
    with c2:
        st.metric("Total Credits", f"{total_credits:.1f}")

    st.subheader("Rechenlogik")
    st.markdown(
        """
        **Fachnote:**  
        \[
        \text{Fachnote} = \sum (\text{Teilnote} \times \text{Prozentanteil})
        \]

        **Gesamtschnitt:**  
        \[
        \text{Gesamtschnitt} = \frac{\sum (\text{Fachnote} \times \text{Credits})}{\sum \text{Credits}}
        \]
        """
    )


st.header("4. Beispiel")
st.markdown(
    """
    Beispiel für **Mathematik**:

    - Prüfung 1: Note 4.5, Gewicht 5%
    - Prüfung 2: Note 5.0, Gewicht 20%
    - Prüfung 3: Note 3.5, Gewicht 5%
    - Prüfung 4: Note 5.5, Gewicht 70%

    Dann wird daraus die **Fachnote Mathematik** berechnet.  
    Hat Mathematik **3 Credits**, dann fliesst ein:

    \[
    \text{Mathe-Beitrag} = \text{Fachnote Mathe} \times 3
    \]

    Dieser Beitrag wird anschliessend mit den Beiträgen der anderen Fächer verrechnet.
    """
)
