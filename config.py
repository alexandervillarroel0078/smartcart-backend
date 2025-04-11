import psycopg2

def conectar_db():
    try:
        conexion = psycopg2.connect(
            host="localhost",
            database="smart_cart",
            user="postgres",
            password=1234
        )
        print("✅ Conexión exitosa a PostgreSQL")
        return conexion
    except Exception as e:
        print("❌ Error al conectar a PostgreSQL:", e)
        return None

# ✅ Clave secreta para JWT
SECRET_KEY = "1234"