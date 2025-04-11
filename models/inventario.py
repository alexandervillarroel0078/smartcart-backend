# models/inventario.py
from config import conectar_db

# Función para registrar entradas y salidas en el inventario
def registrar_movimiento_inventario(id_producto, tipo, cantidad, motivo):
    conexion = conectar_db()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO inventario (id_producto, tipo, cantidad, motivo)
            VALUES (%s, %s, %s, %s)
        """, (id_producto, tipo, cantidad, motivo))

        # Actualizar el stock en productos
        if tipo == 'entrada':
            cursor.execute("""
                UPDATE productos SET stock = stock + %s WHERE id = %s
            """, (cantidad, id_producto))
        elif tipo == 'salida':
            cursor.execute("""
                UPDATE productos SET stock = stock - %s WHERE id = %s
            """, (cantidad, id_producto))

        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al registrar movimiento de inventario:", e)
        return False

# Función para ver productos con bajo stock (por debajo del umbral)
def obtener_alertas_bajo_stock():
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT p.id, p.nombre, p.stock, p.umbral_minimo
            FROM productos p
            WHERE p.stock <= p.umbral_minimo
        """)
        productos = cursor.fetchall()
        conexion.close()

        return [
            {
                "id": p[0],
                "nombre": p[1],
                "stock": p[2],
                "umbral_minimo": p[3]
            } for p in productos
        ]
    except Exception as e:
        print("❌ Error al obtener alertas de bajo stock:", e)
        return []
