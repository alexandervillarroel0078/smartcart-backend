# 📁 smart_cart_backend/scripts/probar_conexion.py
import psycopg2

try:
    conn = psycopg2.connect(
        database="smart_cart",     # ⚠️ Es el nombre correcto según tu pgAdmin
        user="postgres",           # 👈 cambia si usas otro usuario
        password="1234",           # 👈 cambia por tu contraseña real
        host="localhost",
        port="5432"
    )
    print("✅ Conexión exitosa a PostgreSQL")
    conn.close()

except Exception as e:
    print("❌ Error al conectar a la base de datos:")
    print(e)
