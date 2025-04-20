from config import conectar_db

def obtener_reporte_cliente(id_cliente):
    conexion = conectar_db()
    if conexion is None:
        return None

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT c.fecha, p.monto
            FROM compras c
            JOIN pagos p ON c.id = p.id_compra
            WHERE c.id_cliente = %s
        """, (id_cliente,))
        datos = cursor.fetchall()
        conexion.close()

        compras = [{"fecha": str(row[0]), "monto": float(row[1])} for row in datos]
        total = sum([compra["monto"] for compra in compras])

        return {
            "cliente_id": id_cliente,
            "total_gastado": total,
            "cantidad_compras": len(compras),
            "detalle": compras
        }

    except Exception as e:
        print("❌ Error al generar reporte:", e)
        return None


def obtener_reporte_por_cliente(id_cliente):
    conexion = conectar_db()
    if conexion is None:
        return None

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT c.id, c.total, c.fecha, p.metodo_pago
            FROM compras c
            LEFT JOIN pagos p ON c.id = p.id_compra
            WHERE c.id_cliente = %s
            ORDER BY c.fecha DESC
        """, (id_cliente,))
        compras = cursor.fetchall()
        conexion.close()

        return [
            {
                "id": c[0],
                "total": float(c[1]),
                "fecha": str(c[2]),
                "metodo_pago": c[3]
            } for c in compras
        ]
    except Exception as e:
        print("❌ Error al generar reporte:", e)
        return None