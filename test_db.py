import psycopg2

try:
    conn = psycopg2.connect(
        dbname="smart_cart_l01l",
        user="admin",
        password="EQBpBS8xOnHs79DgBIYezrIzh0HXuoiJ",
        host="dpg-cvskdn15pdvs73boakng-a.oregon-postgres.render.com",
        port="5432"
    )
    print("✅ Conexión exitosa a la base de datos de Render.")
    conn.close()
except Exception as e:
    print("❌ Error al conectar:", e)
