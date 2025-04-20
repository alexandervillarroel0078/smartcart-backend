import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # Esto carga .env en desarrollo

def conectar_db():
    try:
        db_url = os.getenv("DATABASE_URL")
        print("📡 Valor de DATABASE_URL:", db_url)

        if not db_url:
            raise Exception("❌ DATABASE_URL no está definida")

        conexion = psycopg2.connect(db_url)
        print("✅ Conectado a PostgreSQL en Render")
        return conexion
    except Exception as e:
        print("❌ Error al conectar con la base en Render:", e)
        return None

# 🔐 Asegurate de que esto esté FUERA de la función
SECRET_KEY = "1234"
