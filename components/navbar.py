"""Barra superior / encabezado para el sistema."""

import streamlit as st

from components.styles import load_global_styles

# Mismo set de iconos SVG minimalistas usado en el resto del sistema
NAVBAR_ICONS = {
    "dashboard": '<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
    "inbox": '<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11Z"/>',
    "box": '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.73Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "cart": '<circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>',
    "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
}

DEFAULT_ICON = "dashboard"


def _svg_icon(name: str, size: int = 26, color: str = "#1E40AF") -> str:
    path = NAVBAR_ICONS.get(name, NAVBAR_ICONS[DEFAULT_ICON])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
    )


def render_navbar(titulo: str, subtitulo: str = "", icono: str = "") -> None:
    load_global_styles()

    icon_key = icono if icono in NAVBAR_ICONS else DEFAULT_ICON
    icon_html = _svg_icon(icon_key)

    st.markdown(
        f"""
        <div style='background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%); 
                    border-radius: 1rem; 
                    padding: 1.5rem 2rem; 
                    margin-bottom: 1.5rem;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
                    border: 1px solid #E2E8F0;'>
            <div style='display: flex; align-items: center; gap: 1rem;'>
                <div style='width: 48px; height: 48px; border-radius: 0.75rem;
                            background: #EFF6FF; flex-shrink: 0;
                            display: flex; align-items: center; justify-content: center;'>
                    {icon_html}
                </div>
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