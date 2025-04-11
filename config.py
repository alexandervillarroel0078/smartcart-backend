import os
import psycopg2

def conectar_db():
    try:
        db_url = os.getenv("DATABASE_URL")  # Render provee esta variable
        conexion = psycopg2.connect(db_url)
        print("✅ Conectado a PostgreSQL en Render")
        return conexion
    except Exception as e:
        print("❌ Error al conectar con la base en Render:", e)
        return None

# ✅ Clave secreta para JWT
SECRET_KEY = "1234"
