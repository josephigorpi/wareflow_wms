"""Gestor de creación, inicialización y operaciones CRUD de la base de datos WareFlow WMS."""

import sqlite3
from pathlib import Path

from config.settings import DB_PATH


def _get_db_path() -> Path:
    db_file = Path(DB_PATH)
    if not db_file.parent.exists():
        db_file.parent.mkdir(parents=True, exist_ok=True)
    return db_file


def get_connection() -> sqlite3.Connection:
    db_file = _get_db_path()
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    return connection


def execute_script(script_path: str) -> None:
    connection = get_connection()
    try:
        with open(script_path, "r", encoding="utf-8") as script_file:
            sql_script = script_file.read()
        connection.executescript(sql_script)
        connection.commit()
    finally:
        connection.close()


def fetch_one(query: str, params: tuple = ()):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    finally:
        connection.close()


def fetch_all(query: str, params: tuple = ()):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        connection.close()


def execute(query: str, params: tuple = ()) -> int:
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.commit()
        return cursor.rowcount
    finally:
        connection.close()


def insert(table: str, data: dict) -> int:
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data])
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(query, tuple(data.values()))
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def update(table: str, data: dict, where_clause: str, where_params: tuple = ()) -> int:
    set_clause = ", ".join([f"{column} = ?" for column in data.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    params = tuple(data.values()) + tuple(where_params)
    return execute(query, params)


def delete(table: str, where_clause: str, where_params: tuple = ()) -> int:
    query = f"DELETE FROM {table} WHERE {where_clause}"
    return execute(query, where_params)


def initialize_database(schema_path: str = "database/schema.sql", seed_path: str = "database/seed_data.sql") -> None:
    """Crea el esquema y carga los datos iniciales de la base de datos."""
    execute_script(schema_path)
    execute_script(seed_path)


def reset_database(schema_path: str = "database/schema.sql") -> None:
    """Recrea la base de datos desde el esquema, eliminando la base existente si es necesario."""
    db_file = _get_db_path()
    if db_file.exists():
        db_file.unlink()
    execute_script(schema_path)
