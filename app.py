import json
from pathlib import Path

import pandas as pd
import streamlit as st


# --------------------------------------------------
# Konfiguration
# --------------------------------------------------
st.set_page_config(
    page_title="Semesternoten",
    page_icon=":material/school:",
    layout="wide",
)

DATEI_PFAD = Path.home() / "SWITCHdrive" / "semesternoten" / "daten" / "faecher.json"


# --------------------------------------------------
# Daten laden / speichern
# --------------------------------------------------
def lade_faecher():
    DATEI_PFAD.parent.mkdir(parents=True, exist_ok=True)

    if not DATEI_PFAD.exists():
        return []

    try:
        with open(DATEI_PFAD, "r", encoding="utf-8") as f:
            daten = json.load(f)

        if isinstance(daten, list):
            return daten
        return []

    except Exception:
        return []


def speichere_faecher(faecher):
    DATEI_PFAD.parent.mkdir(parents=True, exist_ok=True)

    with open(DATEI_PFAD, "w", encoding="utf-8") as f:
        json.dump(faecher, f, ensure_ascii=False, indent=2)


# --------------------------------------------------
# Berechnungen
# --------------------------------------------------
def pruefungen_gewicht_summe(pruefungen):
    return sum(float(p.get("gewicht", 0)) for p in pruefungen)


def berechne_fachnote(pruefungen):
    if not pruefungen:
        return None

    gewicht_summe = pruefungen_gewicht_summe(pruefungen)
    if gewicht_summe == 0:
        return None

    fachnote = sum(
        float(p.get("note", 0)) * (float(p.get("gewicht", 0)) / 100)
        for p in pruefungen
    )
    return fachnote


def berechne_gesamtschnitt(faecher):
    gueltige_faecher = []

    for fach in faecher:
        pruefungen = fach.get("pruefungen", [])
        fachnote = berechne_fachnote(pruefungen)
        credits = float(fach.get("credits", 0))

        if fachnote is not None and credits > 0:
            gueltige_faecher.append(
                {
                    "fachnote": fachnote,
                    "credits": credits,
                }
            )

    total_credits = sum(f["credits"] for f in gueltige_faecher)

    if total_credits == 0:
        return None, 0.0

    gewichtete_summe = sum(f["fachnote"] * f["credits"] for f in gueltige_faecher)
    gesamtschnitt = gewichtete_summe / total_credits
    return gesamtschnitt, total_credits


# --------------------------------------------------
# Session State
# --------------------------------------------------
if "faecher" not in st.session_state:
    st.session_state.faecher = lade_faecher()


def speichern_und_neuladen():
    speichere_faecher(st.session_state.faecher)
    st.session_state.faecher = lade_faecher()


# --------------------------------------------------
# Sidebar Navigation
# --------------------------------------------------
st.sidebar.title("Semesternoten")
seite = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Fach erfassen",
        "Prüfungen erfassen",
        "Fächerübersicht",
        "Gesamtauswertung",
    ],
)


# --------------------------------------------------
# Dashboard
# --------------------------------------------------
if seite == "Dashboard":
    st.title("Dashboard")
    st.caption("Übersicht über deine Semesterleistungen")

    faecher = st.session_state.faecher
    anzahl_faecher = len(faecher)
    gesamtschnitt, total_credits = berechne_gesamtschnitt(faecher)

    vollstaendige_faecher = 0
    unvollstaendige_faecher = 0

    for fach in faecher:
        fachnote = berechne_fachnote(fach.get("pruefungen", []))
        if fachnote is None:
            unvollstaendige_faecher += 1
        else:
            vollstaendige_faecher += 1

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Fächer", anzahl_faecher)

    with c2:
        st.metric("Vollständig", vollstaendige_faecher)

    with c3:
        st.metric("Credits", f"{total_credits:.1f}")

    with c4:
        st.metric(
            "Gesamtschnitt",
            f"{gesamtschnitt:.2f}" if gesamtschnitt is not None else "-",
        )

    st.markdown("## Letzte Fächer")

    if not faecher:
        st.info("Noch keine Fächer erfasst.")
    else:
        for fach in faecher[-5:]:
            fachnote = berechne_fachnote(fach.get("pruefungen", []))
            if fachnote is not None:
                st.write(
                    f"**{fach.get('name', '-')}** · {fach.get('semester', '-')} · "
                    f"{fach.get('credits', 0)} Credits · Fachnote: {fachnote:.2f}"
                )
            else:
                st.write(
                    f"**{fach.get('name', '-')}** · {fach.get('semester', '-')} · "
                    f"{fach.get('credits', 0)} Credits · Fachnote: -"
                )


# --------------------------------------------------
# Fach erfassen
# --------------------------------------------------
elif seite == "Fach erfassen":
    st.title("Fach erfassen")

    with st.form("fach_form", clear_on_submit=True):
        name = st.text_input("Fachname", placeholder="z. B. Mathematik")
        semester = st.text_input("Semester", placeholder="z. B. HS25")
        credits = st.number_input("Credits", min_value=0.0, step=0.5, value=3.0)
        modulgruppe = st.text_input(
            "Modulgruppe (optional)",
            placeholder="z. B. Grundlagen",
        )

        submitted = st.form_submit_button("Fach speichern")

        if submitted:
            if not name.strip():
                st.error("Bitte einen Fachnamen eingeben.")
            else:
                fach_existiert = any(
                    f.get("name", "").strip().casefold() == name.strip().casefold()
                    and f.get("semester", "").strip().casefold() == semester.strip().casefold()
                    for f in st.session_state.faecher
                )

                if fach_existiert:
                    st.error("Dieses Fach existiert in diesem Semester bereits.")
                else:
                    st.session_state.faecher.append(
                        {
                            "name": name.strip(),
                            "semester": semester.strip(),
                            "credits": float(credits),
                            "modulgruppe": modulgruppe.strip(),
                            "pruefungen": [],
                        }
                    )
                    speichern_und_neuladen()
                    st.success("Fach gespeichert.")


# --------------------------------------------------
# Prüfungen erfassen
# --------------------------------------------------
elif seite == "Prüfungen erfassen":
    st.title("Prüfungen erfassen")

    faecher = st.session_state.faecher

    if not faecher:
        st.info("Bitte zuerst ein Fach erfassen.")
        st.stop()

    optionen = [f"{fach['name']} ({fach['semester']})" for fach in faecher]

    auswahl = st.selectbox("Fach auswählen", optionen)
    index = optionen.index(auswahl)
    fach = faecher[index]

    st.markdown(f"### {fach['name']}")
    st.write(f"Semester: {fach['semester']}")
    st.write(f"Credits: {fach['credits']}")

    with st.form("pruefung_form", clear_on_submit=True):
        pruefungsname = st.text_input("Bezeichnung", placeholder="z. B. Midterm")
        note = st.number_input(
            "Note",
            min_value=1.0,
            max_value=6.0,
            value=4.0,
            step=0.1,
            format="%.1f",
        )
        gewicht = st.number_input(
            "Gewichtung in %",
            min_value=0.0,
            max_value=100.0,
            value=25.0,
            step=1.0,
            format="%.1f",
        )

        submitted = st.form_submit_button("Prüfung hinzufügen")

        if submitted:
            if not pruefungsname.strip():
                st.error("Bitte eine Bezeichnung eingeben.")
            else:
                fach["pruefungen"].append(
                    {
                        "name": pruefungsname.strip(),
                        "note": float(note),
                        "gewicht": float(gewicht),
                    }
                )
                speichern_und_neuladen()
                st.success("Prüfung hinzugefügt.")

    st.markdown("## Bereits erfasste Prüfungen")

    pruefungen = fach.get("pruefungen", [])

    if not pruefungen:
        st.info("Noch keine Prüfungen erfasst.")
    else:
        for i, pruefung in enumerate(pruefungen):
            c1, c2, c3, c4 = st.columns([4, 2, 2, 1])

            with c1:
                st.write(pruefung["name"])
            with c2:
                st.write(f"Note: {pruefung['note']:.2f}")
            with c3:
                st.write(f"Gewicht: {pruefung['gewicht']:.1f}%")
            with c4:
                if st.button("X", key=f"delete_{index}_{i}"):
                    fach["pruefungen"].pop(i)
                    speichern_und_neuladen()
                    st.rerun()

    gewicht_summe = pruefungen_gewicht_summe(pruefungen)
    fachnote = berechne_fachnote(pruefungen)

    st.markdown("## Zwischenstand")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Gewichtsumme", f"{gewicht_summe:.1f}%")

    with c2:
        st.metric("Aktuelle Fachnote", f"{fachnote:.2f}" if fachnote is not None else "-")

    if abs(gewicht_summe - 100) > 1e-9:
        st.warning("Die Gewichtungen ergeben noch nicht genau 100%.")
    else:
        st.success("Die Gewichtungen ergeben genau 100%.")


# --------------------------------------------------
# Fächerübersicht
# --------------------------------------------------
elif seite == "Fächerübersicht":
    st.title("Fächerübersicht")

    faecher = st.session_state.faecher

    if not faecher:
        st.info("Noch keine Fächer vorhanden.")
        st.stop()

    rows = []
    for fach in faecher:
        pruefungen = fach.get("pruefungen", [])
        fachnote = berechne_fachnote(pruefungen)
        gewicht_summe = pruefungen_gewicht_summe(pruefungen)

        rows.append(
            {
                "Fach": fach.get("name", ""),
                "Semester": fach.get("semester", ""),
                "Credits": fach.get("credits", 0),
                "Modulgruppe": fach.get("modulgruppe", ""),
                "Prüfungen": len(pruefungen),
                "Prozentsumme": round(gewicht_summe, 1),
                "Fachnote": round(fachnote, 2) if fachnote is not None else None,
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    st.markdown("## Fächer verwalten")

    for idx, fach in enumerate(faecher):
        with st.expander(f"{fach['name']} ({fach['semester']})", expanded=False):
            st.write(f"Credits: {fach['credits']}")
            st.write(f"Modulgruppe: {fach.get('modulgruppe', '-') or '-'}")

            pruefungen = fach.get("pruefungen", [])
            if pruefungen:
                pdf = pd.DataFrame(pruefungen)
                pdf = pdf.rename(
                    columns={
                        "name": "Prüfung",
                        "note": "Note",
                        "gewicht": "Gewicht %",
                    }
                )
                st.dataframe(pdf, use_container_width=True)
            else:
                st.info("Keine Prüfungen vorhanden.")

            if st.button("Fach löschen", key=f"fach_delete_{idx}"):
                st.session_state.faecher.pop(idx)
                speichern_und_neuladen()
                st.rerun()


# --------------------------------------------------
# Gesamtauswertung
# --------------------------------------------------
elif seite == "Gesamtauswertung":
    st.title("Gesamtauswertung")

    faecher = st.session_state.faecher

    if not faecher:
        st.info("Noch keine Fächer vorhanden.")
        st.stop()

    rows = []
    for fach in faecher:
        pruefungen = fach.get("pruefungen", [])
        fachnote = berechne_fachnote(pruefungen)
        gewicht_summe = pruefungen_gewicht_summe(pruefungen)
        credits = float(fach.get("credits", 0))

        rows.append(
            {
                "Fach": fach.get("name", ""),
                "Semester": fach.get("semester", ""),
                "Credits": credits,
                "Prozentsumme": round(gewicht_summe, 1),
                "Fachnote": round(fachnote, 2) if fachnote is not None else None,
                "Note x Credits": round(fachnote * credits, 2) if fachnote is not None else None,
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    gesamtschnitt, total_credits = berechne_gesamtschnitt(faecher)

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Gesamtschnitt", f"{gesamtschnitt:.2f}" if gesamtschnitt is not None else "-")
    with c2:
        st.metric("Total Credits", f"{total_credits:.1f}")

    st.markdown(
        r"""
### Rechenlogik

**Fachnote**

\[
\text{Fachnote} = \sum (\text{Teilnote} \times \text{Gewichtung})
\]

**Gesamtschnitt**

\[
\text{Gesamtschnitt} = \frac{\sum (\text{Fachnote} \times \text{Credits})}{\sum \text{Credits}}
\]
"""
    )