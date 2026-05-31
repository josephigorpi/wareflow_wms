"""Componentes de diálogos y confirmaciones para WareFlow WMS."""

import streamlit as st


def confirm_dialog(titulo: str, mensaje: str, key: str) -> bool:
    st.write(f"### {titulo}")
    st.write(mensaje)
    return st.button("Confirmar", key=key)
