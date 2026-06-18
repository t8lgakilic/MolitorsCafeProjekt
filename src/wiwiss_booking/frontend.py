from __future__ import annotations

import os
from datetime import date
from pathlib import Path

Path("work/matplotlib-cache").mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", "work/matplotlib-cache")

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st


API_URL = os.getenv("WIWISS_API_URL", "http://127.0.0.1:8000")
FU_GREEN = "#CCFF00"
DEEP_TEAL = "#004659"
BURGUNDY = "#813353"
SKY_BLUE = "#00A4D1"
CORAL = "#E57050"
SAGE = "#58756A"
FENERBAHCE_NAVY = "#002D62"
EXPENSE_RED = "#FF0000"
BLACK = "#000000"
WHITE = "#ffffff"
LIGHT_GRAY = "#f6f8f5"
TYPE_LABELS = {"income": "Einnahme", "expense": "Ausgabe"}
TYPE_VALUES = {"Einnahme": "income", "Ausgabe": "expense"}
CHART_PALETTE = [FU_GREEN, DEEP_TEAL, BURGUNDY, SKY_BLUE, CORAL, SAGE]
SECONDARY_CHART_PALETTE = [DEEP_TEAL, BURGUNDY, SKY_BLUE, CORAL, SAGE]


def style_axis(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(DEEP_TEAL)
    ax.spines["bottom"].set_color(DEEP_TEAL)
    ax.tick_params(colors=DEEP_TEAL)
    ax.title.set_color(DEEP_TEAL)
    ax.yaxis.label.set_color(DEEP_TEAL)
    ax.set_facecolor(WHITE)


def apply_theme() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {WHITE};
            color: {DEEP_TEAL};
        }}

        h1, h2, h3, label, p {{
            color: {DEEP_TEAL};
        }}

        h1 {{
            border-bottom: 4px solid {FU_GREEN};
            padding-bottom: 0.35rem;
        }}

        div[data-testid="stMetric"] {{
            background: {LIGHT_GRAY};
            border-left: 5px solid {FU_GREEN};
            padding: 1rem;
        }}

        div[data-testid="stMetricValue"] {{
            color: {DEEP_TEAL};
        }}

        div[data-testid="stButton"] > button,
        div[data-testid="stButton"] > button *,
        button[kind="primary"],
        button[kind="primary"] * {{
            background: {DEEP_TEAL};
            border-color: {DEEP_TEAL};
            color: {WHITE};
        }}

        div[data-testid="stButton"] > button:hover,
        div[data-testid="stButton"] > button:hover *,
        button[kind="primary"]:hover,
        button[kind="primary"]:hover * {{
            background: {BURGUNDY};
            border-color: {BURGUNDY};
            color: {WHITE};
        }}

        div[data-testid="stFormSubmitButton"] > button,
        div[data-testid="stFormSubmitButton"] > button *,
        div[data-testid="stFormSubmitButton"] button[kind="primary"],
        div[data-testid="stFormSubmitButton"] button[kind="primary"] * {{
            background: {FENERBAHCE_NAVY};
            border-color: {FENERBAHCE_NAVY};
            color: {WHITE};
        }}

        div[data-testid="stFormSubmitButton"] > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover *,
        div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover,
        div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover * {{
            background: {DEEP_TEAL};
            border-color: {DEEP_TEAL};
            color: {WHITE};
        }}

        div[data-baseweb="button-group"] {{
            border-color: {BLACK};
        }}

        div[data-baseweb="button-group"] button {{
            background: {WHITE} !important;
            border-color: {BLACK} !important;
            border-width: 1px !important;
            color: {FENERBAHCE_NAVY} !important;
        }}

        div[data-baseweb="button-group"] button * {{
            background: transparent !important;
            color: {FENERBAHCE_NAVY} !important;
        }}

        div[data-baseweb="button-group"] button + button {{
            border-left-width: 1px !important;
            border-left-color: {BLACK} !important;
            box-shadow: none !important;
        }}

        div[data-baseweb="button-group"] button:nth-of-type(1)[kind="segmented_controlActive"] {{
            background: {FU_GREEN} !important;
            border-color: {BLACK} !important;
            color: {DEEP_TEAL} !important;
        }}

        div[data-baseweb="button-group"] button:nth-of-type(1)[kind="segmented_controlActive"] * {{
            color: {DEEP_TEAL} !important;
        }}

        div[data-baseweb="button-group"] button:nth-of-type(2)[kind="segmented_controlActive"] {{
            background: {EXPENSE_RED} !important;
            border-color: {BLACK} !important;
            color: {WHITE} !important;
        }}

        div[data-baseweb="button-group"] button:nth-of-type(2)[kind="segmented_controlActive"] * {{
            color: {WHITE} !important;
        }}

        div[data-baseweb="button-group"] button:nth-of-type(1):hover,
        div[data-baseweb="button-group"] button:nth-of-type(1):hover * {{
            background: {FU_GREEN} !important;
            border-color: {BLACK} !important;
            color: {DEEP_TEAL} !important;
        }}

        div[data-baseweb="button-group"] button:nth-of-type(2):hover,
        div[data-baseweb="button-group"] button:nth-of-type(2):hover * {{
            background: {EXPENSE_RED} !important;
            border-color: {BLACK} !important;
            color: {WHITE} !important;
        }}

        div[data-baseweb="tab-list"] button[aria-selected="true"] {{
            color: {DEEP_TEAL};
            border-bottom-color: {FU_GREEN};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def api_get(path: str, **params):
    response = requests.get(f"{API_URL}{path}", params=params or None, timeout=10)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict):
    response = requests.post(f"{API_URL}{path}", json=payload, timeout=10)
    if response.status_code == 422:
        detail = response.json().get("detail", [])
        messages = []
        for error in detail:
            field = error.get("loc", ["Feld"])[-1]
            message = error.get("msg", "ungültiger Wert")
            messages.append(f"{field}: {message}")
        raise ValueError("; ".join(messages) or "Die Eingaben konnten nicht gespeichert werden.")
    response.raise_for_status()
    return response.json()


def api_delete(path: str):
    response = requests.delete(f"{API_URL}{path}", timeout=10)
    response.raise_for_status()
    return response.json()


def show_booking_form() -> None:
    with st.form("booking_form", clear_on_submit=True):
        left, right = st.columns(2)
        booking_date = left.date_input("Buchungsdatum", value=date.today())
        amount = right.number_input("Betrag", min_value=0.01, step=10.0, format="%.2f")
        booking_type_label = left.segmented_control("Typ", ["Einnahme", "Ausgabe"], default="Einnahme")
        category = right.text_input("Kategorie", placeholder="z.B. Kaffeeumsatz, Gebäck, Miete, Personal, Einkauf")
        description = st.text_input("Beschreibung", placeholder="Optional, sonst: Keine Beschreibung")
        is_recurring = st.checkbox("Periodische Zahlung")
        months = st.number_input("Anzahl Monate", min_value=2, max_value=24, value=6, step=1)
        submitted = st.form_submit_button("Buchung speichern", type="primary")

    if submitted:
        clean_category = category.strip()
        clean_description = description.strip() or "Keine Beschreibung"
        if len(clean_category) < 2:
            st.error("Bitte eine Kategorie mit mindestens 2 Zeichen eingeben.")
            return
        payload = {
            "booking_date": booking_date.isoformat(),
            "amount": f"{float(amount):.2f}",
            "booking_type": TYPE_VALUES[booking_type_label],
            "category": clean_category,
            "description": clean_description,
        }
        try:
            if is_recurring:
                inserted = api_post("/bookings/recurring", {"booking": payload, "months": int(months)})
            else:
                inserted = [api_post("/bookings", payload)]
        except ValueError as error:
            st.error(f"Buchung konnte nicht gespeichert werden: {error}")
            return
        except requests.RequestException:
            st.error("Buchung konnte nicht gespeichert werden. Bitte prüfen, ob das Backend läuft.")
            return

        if len(inserted) == 1:
            st.success("Buchung gespeichert.")
        else:
            st.success(f"{len(inserted)} periodische Buchungen gespeichert.")


def show_bookings() -> None:
    try:
        bookings = api_get("/bookings")
    except requests.RequestException:
        st.error("Buchungen konnten nicht geladen werden. Bitte Seite neu laden oder Backend prüfen.")
        return

    if not bookings:
        st.info("Noch keine Buchungen vorhanden.")
        return

    booking_options = {
        f"#{booking['id']} | {booking['booking_date']} | {TYPE_LABELS[booking['booking_type']]} | {booking['category']} | {booking['amount']} EUR": booking["id"]
        for booking in bookings
    }
    left, right = st.columns([3, 1])
    selected_booking = left.selectbox("Buchung löschen", options=list(booking_options.keys()))
    if right.button("Löschen"):
        try:
            api_delete(f"/bookings/{booking_options[selected_booking]}")
        except requests.RequestException:
            st.error("Buchung konnte nicht gelöscht werden. Bitte Seite neu laden oder Backend prüfen.")
            return
        st.success("Buchung gelöscht.")
        st.rerun()

    df = pd.DataFrame(bookings)
    df = df[["id", "booking_date", "booking_type", "category", "amount", "description"]]
    df["booking_type"] = df["booking_type"].map(TYPE_LABELS).fillna(df["booking_type"])
    df = df.rename(
        columns={
            "id": "ID",
            "booking_date": "Datum",
            "booking_type": "Typ",
            "category": "Kategorie",
            "amount": "Betrag",
            "description": "Beschreibung",
        }
    )
    st.dataframe(df, width="stretch", hide_index=True)


def show_income_statement() -> None:
    left, right = st.columns(2)
    start_date = left.date_input("Von", value=None)
    end_date = right.date_input("Bis", value=date.today())
    params = {"end_date": end_date.isoformat()}
    if start_date:
        params["start_date"] = start_date.isoformat()

    try:
        statement = api_get("/analytics/income-statement", **params)
    except requests.RequestException:
        st.error("GuV konnte nicht geladen werden. Bitte Seite neu laden oder Backend prüfen.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Einnahmen", f"{statement['income']:,.2f} EUR")
    col2.metric("Ausgaben", f"{statement['expenses']:,.2f} EUR")
    col3.metric("Gewinn", f"{statement['profit']:,.2f} EUR")

    tax_col1, tax_col2 = st.columns(2)
    tax_col1.metric("Umsatz-Kategorien", f"{statement['taxable_umsatz']:,.2f} EUR")
    tax_col2.metric("ESt-Schätzung 2026", f"{statement['estimated_income_tax_2026']:,.2f} EUR")
    st.caption(
        "Vereinfachte Schätzung: Einnahmen aus Kategorien mit 'umsatz' werden als zu versteuerndes Einkommen "
        "angenommen. Betriebsausgaben, Freibeträge außerhalb des Tarifs, Solidaritätszuschlag und Kirchensteuer "
        "werden hier nicht zusätzlich berechnet."
    )

    categories = pd.DataFrame(statement["by_category"])
    if not categories.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        labels = categories["category"] + " (" + categories["booking_type"].map(TYPE_LABELS) + ")"
        largest_index = int(categories["amount"].idxmax())
        colors = [
            FU_GREEN if row_index == largest_index else SECONDARY_CHART_PALETTE[position % len(SECONDARY_CHART_PALETTE)]
            for position, row_index in enumerate(categories.index)
        ]
        ax.bar(labels, categories["amount"], color=colors)
        ax.set_title("Summe nach Kategorie")
        ax.set_ylabel("EUR")
        ax.tick_params(axis="x", rotation=35)
        style_axis(ax)
        fig.patch.set_facecolor(WHITE)
        fig.tight_layout()
        st.pyplot(fig)


def show_dashboard() -> None:
    try:
        dashboard = api_get("/analytics/dashboard")
    except requests.RequestException:
        st.error("Dashboard konnte nicht geladen werden. Bitte Seite neu laden oder Backend prüfen.")
        return

    if dashboard["total_bookings"] == 0:
        st.info("Dashboard erscheint, sobald Buchungen vorhanden sind.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Buchungen", dashboard["total_bookings"])
    col2.metric("Durchschnitt", f"{dashboard['average_booking']:,.2f} EUR")
    col3.metric("Größte Ausgabe", dashboard["largest_expense_category"] or "-")
    col4.metric("Bester Monat", dashboard["best_month"] or "-")

    monthly = pd.DataFrame(dashboard["monthly"])
    categories = pd.DataFrame(dashboard["categories"])

    if not monthly.empty:
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(monthly["month"], monthly["income"], color=SKY_BLUE, marker="o", linewidth=2, label="Einnahmen")
        ax.plot(monthly["month"], monthly["expenses"], color=CORAL, marker="o", linewidth=2, label="Ausgaben")
        ax.bar(monthly["month"], monthly["profit"], color=FU_GREEN, alpha=0.65, label="Gewinn")
        ax.set_title("Monatliche Entwicklung")
        ax.set_ylabel("EUR")
        ax.legend(frameon=False)
        style_axis(ax)
        fig.patch.set_facecolor(WHITE)
        fig.tight_layout()
        st.pyplot(fig)

    if not categories.empty:
        visible_categories = categories.copy()
        visible_categories["booking_type"] = visible_categories["booking_type"].map(TYPE_LABELS)
        visible_categories = visible_categories.rename(
            columns={
                "category": "Kategorie",
                "booking_type": "Typ",
                "amount": "Betrag",
                "share": "Anteil in %",
            }
        )
        st.dataframe(visible_categories, width="stretch", hide_index=True)


def show_forecast() -> None:
    try:
        forecast = api_get("/analytics/forecast", months=3)
    except requests.RequestException:
        st.error("Forecast konnte nicht geladen werden. Bitte Seite neu laden oder Backend prüfen.")
        return

    if not forecast:
        st.info("Forecast erscheint, sobald Buchungen vorhanden sind.")
        return

    df = pd.DataFrame(forecast)
    df = df.rename(columns={"month": "Monat", "expected_profit": "Erwarteter Gewinn"})
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["Monat"], df["Erwarteter Gewinn"], color=SAGE, marker="o", linewidth=2.5)
    ax.axhline(0, color=BURGUNDY, linewidth=1)
    ax.set_title("Forecast für erwarteten Gewinn")
    ax.set_ylabel("EUR")
    style_axis(ax)
    fig.patch.set_facecolor(WHITE)
    fig.tight_layout()
    st.pyplot(fig)
    st.dataframe(df, width="stretch", hide_index=True)


def main() -> None:
    st.set_page_config(page_title="Molitor's Cafe", page_icon="EUR", layout="wide")
    apply_theme()
    st.title("Molitor's Cafe")

    try:
        api_get("/health")
    except requests.RequestException:
        st.error("Backend nicht erreichbar. Bitte FastAPI starten.")
        st.stop()

    tab_new, tab_list, tab_analysis, tab_dashboard, tab_forecast = st.tabs(
        ["Neue Buchung", "Buchungen", "GuV", "Dashboard", "Forecast"]
    )
    with tab_new:
        show_booking_form()
    with tab_list:
        show_bookings()
    with tab_analysis:
        show_income_statement()
    with tab_dashboard:
        show_dashboard()
    with tab_forecast:
        show_forecast()


if __name__ == "__main__":
    main()
