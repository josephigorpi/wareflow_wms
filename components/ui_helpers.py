"""Componentes UI reutilizables para diseño minimalista."""

import streamlit as st


# Iconos SVG minimalistas (estilo line-icon, monocromático)
ICONS = {
    "box": '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.73Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "arrow-down": '<circle cx="12" cy="12" r="10"/><path d="M12 8v8"/><path d="m8 12 4 4 4-4"/>',
    "arrow-up": '<circle cx="12" cy="12" r="10"/><path d="M12 16V8"/><path d="m8 12 4-4 4 4"/>',
    "list": '<path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M3 6h.01"/><path d="M3 12h.01"/><path d="M3 18h.01"/>',
    "bar-chart": '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "inbox": '<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11Z"/>',
    "cart": '<circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>',
    "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
    "file": '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
    "edit": '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>',
    "trash": '<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "filter": '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
    "plus": '<circle cx="12" cy="12" r="10"/><path d="M8 12h8"/><path d="M12 8v8"/>',
    "warehouse": '<path d="M3 22v-8a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v8"/><path d="M15 22v-8a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v8"/><path d="M22 22H2"/><path d="M12 2v20"/><path d="M2 10l10-8 10 8"/><path d="M12 2l-4 4"/><path d="M12 2l4 4"/>',
}


def svg_icon(name: str, size: int = 18, color: str = "#475569") -> str:
    """Genera un icono SVG minimalista."""
    path = ICONS.get(name, ICONS["box"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
    )


def section_title(icon: str, text: str) -> None:
    """Renderiza un título de sección con icono."""
    st.markdown(
        f"""
        <div style='display:flex; align-items:center; gap:0.5rem; margin: 0 0 0.9rem 0;'>
            {svg_icon(icon, 16, "#64748B")}
            <span style='font-size:0.75rem; font-weight:600; color:#64748B;
                         text-transform:uppercase; letter-spacing:0.06em;'>{text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(icon: str, label: str, value: str) -> str:
    """Genera HTML para una tarjeta KPI minimalista."""
    return f"""
        <div style='background:#FFFFFF; border:1px solid #E2E8F0; border-radius:0.65rem;
                     padding:1.1rem 1.25rem; display:flex; align-items:center; gap:0.9rem;'>
            <div style='width:38px; height:38px; border-radius:0.5rem; background:#F1F5F9;
                         display:flex; align-items:center; justify-content:center; flex-shrink:0;'>
                {svg_icon(icon, 18, "#334155")}
            </div>
            <div style='min-width:0;'>
                <p style='margin:0; font-size:0.7rem; font-weight:600; color:#94A3B8;
                           text-transform:uppercase; letter-spacing:0.05em; white-space:nowrap;'>
                    {label}
                </p>
                <p style='margin:0.15rem 0 0 0; font-size:1.5rem; font-weight:700; color:#0F172A;'>
                    {value}
                </p>
            </div>
        </div>
        """


def alert_card(icon: str, title: str, message: str, bg_color: str = "#FFFBEB", 
               border_color: str = "#FDE68A", text_color: str = "#78350F") -> str:
    """Genera HTML para una tarjeta de alerta minimalista."""
    return f"""
        <div style='display:flex; align-items:center; gap:0.75rem; background:{bg_color};
                     border:1px solid {border_color}; border-radius:0.5rem; padding:0.65rem 0.9rem;
                     margin-bottom:0.5rem;'>
            {svg_icon(icon, 16, text_color)}
            <div style='font-size:0.85rem; color:{text_color};'>
                <strong>{title}</strong><br>
                <span style='color:{text_color};'>{message}</span>
            </div>
        </div>
        """


def spacer(height: str = "1.75rem") -> None:
    """Agrega espacio vertical."""
    st.markdown(f"<div style='margin: {height} 0 0 0;'></div>", unsafe_allow_html=True)
