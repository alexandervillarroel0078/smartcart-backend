# models/reportes_compras.py
from config import conectar_db

def obtener_reporte_compras(fecha_inicio=None, fecha_fin=None, nombre=None, nit=None, minimo=None, maximo=None):
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = """
                SELECT 
    c.id, 
    COALESCE(c.nombre_cliente, 'No registrado') AS cliente,
    COALESCE(c.nit_cliente, 'No registrado') AS nit_cliente,
    c.total, 
    c.fecha,
    c.id_carrito
FROM compras c
WHERE 1=1


            """
            valores = []

            if fecha_inicio and fecha_fin:
                query += " AND c.fecha BETWEEN %s AND %s"
                valores.extend([fecha_inicio, fecha_fin])
            if nombre:
                query += " AND LOWER(c.nombre_cliente) LIKE %s"
                valores.append(f"%{nombre.lower()}%")
            if nit:
                query += " AND c.nit_cliente = %s"
                valores.append(nit)
            if minimo:
                query += " AND c.total >= %s"
                valores.append(minimo)
            if maximo:
                query += " AND c.total <= %s"
                valores.append(maximo)

            query += " ORDER BY c.fecha DESC"

            cursor.execute(query, tuple(valores))
            resultados = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]
            conexion.close()

            return [dict(zip(columnas, fila)) for fila in resultados]
        except Exception as e:
            print("\u274c Error en reporte de compras:", e)
            return []
    return []


def obtener_productos_mas_vendidos(fecha_inicio=None, fecha_fin=None, limite=5):
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = """
                SELECT p.nombre AS producto, SUM(dc.cantidad) AS cantidad_vendida
                FROM detalle_carrito dc
                JOIN productos p ON dc.id_producto = p.id
                JOIN carrito c ON dc.id_carrito = c.id
                JOIN compras co ON c.id = co.id_carrito
                WHERE 1=1
            """
            valores = []

            if fecha_inicio and fecha_fin:
                query += " AND co.fecha BETWEEN %s AND %s"
                valores.extend([fecha_inicio, fecha_fin])

            query += """
                GROUP BY p.nombre
                ORDER BY cantidad_vendida DESC
                LIMIT %s
            """
            valores.append(limite)

            cursor.execute(query, tuple(valores))
            resultados = cursor.fetchall()
            conexion.close()

            return [{"producto": r[0], "cantidad_vendida": r[1]} for r in resultados]
        except Exception as e:
            print("❌ Error en productos más vendidos:", e)
            return []
    return []

def obtener_ventas_por_fecha(fecha_inicio=None, fecha_fin=None, agrupacion='dia'):
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            if agrupacion == 'mes':
                query = """
                    SELECT TO_CHAR(fecha, 'YYYY-MM') AS periodo, SUM(total) AS total
                    FROM compras
                    WHERE 1=1
                """
            else:
                query = """
                    SELECT TO_CHAR(fecha, 'YYYY-MM-DD') AS periodo, SUM(total) AS total
                    FROM compras
                    WHERE 1=1
                """

            valores = []
            if fecha_inicio and fecha_fin:
                query += " AND fecha BETWEEN %s AND %s"
                valores.extend([fecha_inicio, fecha_fin])

            query += " GROUP BY periodo ORDER BY periodo"

            cursor.execute(query, tuple(valores))
            resultados = cursor.fetchall()
            conexion.close()

            return [{"fecha": r[0], "total": float(r[1])} for r in resultados]
        except Exception as e:
            print("❌ Error en ventas por fecha:", e)
            return []
    return []





