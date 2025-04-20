# models/inventario.py
from config import conectar_db
import unicodedata



def normalizar(texto):
    if not texto:
        return ''
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode("utf-8")
    return texto.lower().strip()

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


def generar_reporte_inventario():
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        cursor.execute("""
    SELECT p.id, p.nombre, p.modelo, p.precio, p.stock,
           p.umbral_minimo, p.umbral_maximo,
           c.nombre AS categoria
    FROM productos p
    JOIN categorias c ON p.id_categoria = c.id
    ORDER BY p.nombre
""")


        productos = cursor.fetchall()
        conexion.close()

        reporte = []
        for p in productos:
            stock = p[4]
            minimo = p[5] if p[5] is not None else 0
            maximo = p[6] if p[6] is not None else 1  # evitamos división por 0 o None

            if maximo == 0:
                porcentaje = 0
            else:
                porcentaje = (stock / maximo) * 100

            if porcentaje <= 25:
                estado = "Crítico"
            elif porcentaje <= 75:
                estado = "Adecuado"
            elif porcentaje <= 100:
                estado = "Lleno"
            else:
                estado = "Excedido"

            reporte.append({
                "id": p[0],
                "nombre": p[1],
                "modelo": p[2],
                "precio": float(p[3]),
                "stock": stock,
                "umbral_minimo": minimo,
                "umbral_maximo": maximo,
                "categoria": p[7],
                "estado": estado,
                "porcentaje": round(porcentaje, 2)
            })

        return reporte
    except Exception as e:
        print("❌ Error al generar reporte de inventario:", e)
        return []
