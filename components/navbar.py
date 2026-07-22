"""Barra superior / encabezado para el sistema."""

import streamlit as st

from components.styles import load_global_styles


def render_navbar(titulo: str, subtitulo: str = "", icono: str = "") -> None:
    load_global_styles()
    
    # Navbar moderno con gradiente y diseño limpio
    st.markdown(
        f"""
        <div style='background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%); 
                    border-radius: 1rem; 
                    padding: 1.5rem 2rem; 
                    margin-bottom: 1.5rem;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
                    border: 1px solid #E2E8F0;'>
            <div style='display: flex; align-items: center; gap: 1rem;'>
                <span style='font-size: 2.5rem; background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%); 
                            -webkit-background-clip: text; 
                            -webkit-text-fill-color: transparent; 
                            background-clip: text;'>
                    {icono}
                </span>
                <div>
                    <h1 style='margin: 0; font-size: 2rem; font-weight: 700; color: #0F172A; letter-spacing: -1px;'>
                        {titulo}
                    </h1>
                    {f'<p style="margin: 0.25rem 0 0 0; color: #64748B; font-size: 0.95rem; font-weight: 400;">{subtitulo}</p>' if subtitulo else ''}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
