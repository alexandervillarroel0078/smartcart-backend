from config import conectar_db
from datetime import datetime

def registrar_compra(id_carrito, total, id_cliente):
    conexion = conectar_db()
    if conexion is None:
        return None

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO compras (id_carrito, total, id_cliente)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (id_carrito, total, id_cliente))
        id_compra = cursor.fetchone()[0]
        conexion.commit()
        conexion.close()
        return id_compra
    except Exception as e:
        print("❌ Error al registrar compra:", e)
        return None
