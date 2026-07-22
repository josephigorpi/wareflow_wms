"""Script para cargar datos de prueba en la base de datos."""

from database.db_manager import execute_script

if __name__ == "__main__":
    print("Cargando datos de prueba...")
    try:
        execute_script("database/seed_data.sql")
        print("✅ Datos de prueba cargados exitosamente.")
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
