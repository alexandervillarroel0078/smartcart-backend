from config import conectar_db

def registrar_cliente(id_usuario):
    conexion = conectar_db()
    if conexion is None:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO clientes (id_usuario) VALUES (%s)
        """, (id_usuario,))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al registrar cliente:", e)
        return False

def listar_clientes():
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT u.id, u.nombre, u.correo, c.fecha_registro
            FROM clientes c
            JOIN usuarios u ON c.id_usuario = u.id
            ORDER BY c.fecha_registro DESC
        """)
        resultado = cursor.fetchall()
        conexion.close()
        return [
            {
                "id": fila[0],
                "nombre": fila[1],
                "correo": fila[2],
                "fecha_registro": str(fila[3])
            } for fila in resultado
        ]
    except Exception as e:
        print("❌ Error al listar clientes:", e)
        return []

def obtener_historial_compras(id_usuario):
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT c.id, c.fecha, p.nombre, dc.cantidad, dc.precio_unitario,
                   (dc.cantidad * dc.precio_unitario) AS subtotal
            FROM carrito c
            JOIN detalle_carrito dc ON c.id = dc.id_carrito
            JOIN productos p ON dc.id_producto = p.id
            WHERE c.id_usuario = %s AND c.estado = 'cerrado'
            ORDER BY c.fecha DESC
        """, (id_usuario,))
        compras = cursor.fetchall()
        conexion.close()

        return [
            {
                "carrito_id": row[0],
                "fecha": row[1],
                "producto": row[2],
                "cantidad": row[3],
                "precio_unitario": float(row[4]),
                "subtotal": float(row[5])
            } for row in compras
        ]
    except Exception as e:
        print("❌ Error al obtener historial:", e)
        return []

def obtener_reporte_cliente(id_usuario):
    conexion = conectar_db()
    if conexion is None:
        return {}

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) AS total_compras,
                SUM((dc.cantidad * dc.precio_unitario)) AS total_gastado,
                AVG((dc.cantidad * dc.precio_unitario)) AS promedio
            FROM carrito c
            JOIN detalle_carrito dc ON c.id = dc.id_carrito
            WHERE c.id_usuario = %s AND c.estado = 'cerrado'
        """, (id_usuario,))
        resultado = cursor.fetchone()
        conexion.close()

        return {
            "total_compras": int(resultado[0]),
            "total_gastado": float(resultado[1]) if resultado[1] else 0,
            "promedio_por_compra": float(resultado[2]) if resultado[2] else 0
        }
    except Exception as e:
        print("❌ Error al obtener reporte del cliente:", e)
        return {}
