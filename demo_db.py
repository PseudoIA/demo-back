from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Obtener la URL de la base de datos desde el .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear el engine de conexión
engine = create_engine(DATABASE_URL)

def listar_tablas():
    """Muestra todas las tablas en la base de datos"""
    inspector = inspect(engine)
    tablas = inspector.get_table_names()

    if tablas:
        print("📌 Tablas en la base de datos:")
        for tabla in tablas:
            print(f" - {tabla}")
    else:
        print("⚠️ No se encontraron tablas en la base de datos.")

if __name__ == "__main__":
    listar_tablas()
