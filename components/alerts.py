"""Mensajes visuales estandarizados para WareFlow WMS."""

import streamlit as st


def alert_success(message: str) -> None:
    st.success(message)


def alert_error(message: str) -> None:
    st.error(message)


def alert_warning(message: str) -> None:
    st.warning(message)


def alert_info(message: str) -> None:
    st.info(message)
