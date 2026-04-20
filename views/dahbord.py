import streamlit as st

st.title("📊 Semester-Dashboard")

user_data = st.session_state.current_notes

if not user_data:
    st.info("Willkommen! Gehe zu 'Fächer erfassen', um deine ersten Module einzutragen.")
else:
    # --- Reihe 1: Die wichtigsten Kennzahlen ---
    total_credits = sum(info['credits'] for info in user_data.values())
    num_subjects = len(user_data)
    
    # Berechnung abgeschlossene Credits
    done_credits = sum(info['credits'] for info in user_data.values() 
                       if sum(e['weight'] for e in info['exams']) == 100)

    st.subheader("Auf einen Blick")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Erfasste Fächer", num_subjects)
    with col2:
        st.metric("Total Credits", f"{total_credits} ECTS")
    with col3:
        progress = (done_credits / total_credits * 100) if total_credits > 0 else 0
        st.metric("Fortschritt", f"{progress:.0f}%", help="Prozent der Fächer, die zu 100% bewertet sind")

    st.divider()

    # --- Reihe 2: Kachel-Ansicht der Fächer ---
    st.subheader("Deine Module")
    
    # Wir erstellen ein Raster (Grid) mit 3 Spalten für die Kacheln
    cols = st.columns(3)
    
    for i, (name, info) in enumerate(user_data.items()):
        # Bestimme, in welche Spalte die Kachel kommt
        col = cols[i % 3]
        
        with col:
            # HTML/CSS für eine schöne Kachel-Optik
            exams = info['exams']
            total_w = sum(e['weight'] for e in exams)
            
            # Farbe basierend auf Fortschritt
            border_color = "#4CAF50" if total_w == 100 else "#FFA500"
            
            # Kachel-Container
            with st.container(border=True):
                st.markdown(f"### {name}")
                st.write(f"**Credits:** {info['credits']}")
                
                if total_w > 0:
                    current_avg = sum(e['grade'] * e['weight'] for e in exams) / total_w
                    st.write(f"**Schnitt:** {current_avg:.2f}")
                else:
                    st.write("*Noch keine Noten*")
                
                # Fortschrittsbalken innerhalb der Kachel
                st.progress(total_w / 100)
                st.caption(f"Fortschritt: {total_w}%")

    # --- Optionale Grafik ---
    if total_credits > 0:
        st.divider()
        st.write("### Semester-Auslastung")
        # Kleiner visueller Balken für das gesamte Semester
        st.progress(done_credits / total_credits)