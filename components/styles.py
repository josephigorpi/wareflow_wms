"""Carga estilos CSS globales para WareFlow WMS."""

from pathlib import Path

import streamlit as st


def load_global_styles() -> None:
    css_path = Path(__file__).resolve().parent.parent / "assets" / "styles" / "custom.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
