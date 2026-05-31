"""Formularios reutilizables para WareFlow WMS."""

import streamlit as st


def input_text(label: str, key: str, required: bool = True, max_length: int = None) -> str:
    return st.text_input(label, key=key)


def input_number(label: str, key: str, min_val: int = 0, max_val: int = None) -> int:
    return st.number_input(label, key=key, min_value=min_val, max_value=max_val if max_val is not None else 999999)


def input_select(label: str, key: str, options=None, placeholder: str = "Seleccione..."):
    if options is None:
        options = []
    return st.selectbox(label, options, key=key)


def input_date(label: str, key: str):
    return st.date_input(label, key=key)


def form_submit_button(label: str = "Guardar", key: str = None) -> bool:
    return st.button(label, key=key)
