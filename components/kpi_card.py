"""Tarjetas KPI para WareFlow WMS."""

import streamlit as st


def render_kpi_card(titulo: str, valor, unidad: str = "", delta: float = None, color: str = "blue", icono: str = "") -> None:
    st.metric(label=f"{icono} {titulo}", value=f"{valor} {unidad}".strip(), delta=f"{delta}%" if delta is not None else None)
