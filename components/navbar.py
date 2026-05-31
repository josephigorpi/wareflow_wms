"""Barra superior / encabezado para el sistema."""

import streamlit as st

from components.styles import load_global_styles


def render_navbar(titulo: str, subtitulo: str = "", icono: str = "") -> None:
    load_global_styles()

    st.markdown(
        f"""
        <div class="navbar">
            <div class="navbar-body">
                <span class="navbar-icon">{icono}</span>
                <div>
                    <h1 class="navbar-title">{titulo}</h1>
                    {f'<p class="navbar-subtitle">{subtitulo}</p>' if subtitulo else ''}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<hr class='navbar-divider' />", unsafe_allow_html=True)
