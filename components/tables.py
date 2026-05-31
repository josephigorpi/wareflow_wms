"""Tablas estándar reutilizables para WareFlow WMS."""

import streamlit as st
import pandas as pd


def render_table(df: pd.DataFrame, key: str = None) -> None:
    st.dataframe(df, use_container_width=True)


def render_table_editable(df: pd.DataFrame, key: str) -> pd.DataFrame:
    return st.experimental_data_editor(df, key=key)
