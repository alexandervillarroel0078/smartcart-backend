# models/detalle_carrito.py
from config import conectar_db

def agregar_producto(id_carrito, id_producto, cantidad, precio_unitario):
    conexion = conectar_db()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()

        # Verificar si el producto ya está en el carrito
        cursor.execute("""
            SELECT id, cantidad FROM detalle_carrito
            WHERE id_carrito = %s AND id_producto = %s
        """, (id_carrito, id_producto))
        existente = cursor.fetchone()

        if existente:
            # Ya existe → actualizar la cantidad sumando
            id_detalle = existente[0]
            cantidad_actual = existente[1]
            nueva_cantidad = cantidad_actual + cantidad
            cursor.execute("""
                UPDATE detalle_carrito
                SET cantidad = %s
                WHERE id = %s
            """, (nueva_cantidad, id_detalle))
        else:
            # No existe → insertar nuevo
            cursor.execute("""
                INSERT INTO detalle_carrito (id_carrito, id_producto, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
            """, (id_carrito, id_producto, cantidad, precio_unitario))

        conexion.commit()
        conexion.close()
        return True

    except Exception as e:
        print("❌ Error al agregar producto al carrito:", e)
        return False

def listar_productos_carrito(id_carrito):
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT dc.id, p.nombre, dc.cantidad, dc.precio_unitario, (dc.cantidad * dc.precio_unitario) AS subtotal
            FROM detalle_carrito dc
            JOIN productos p ON dc.id_producto = p.id
            WHERE dc.id_carrito = %s
        """, (id_carrito,))
        productos = cursor.fetchall()
        conexion.close()
        return [
            {
                "id": p[0],
                "producto": p[1],
                "cantidad": p[2],
                "precio_unitario": float(p[3]),
                "subtotal": float(p[4])
            } for p in productos
        ]
    except Exception as e:
        print("❌ Error al listar productos del carrito:", e)
        return []

def eliminar_producto(id_detalle):
    conexion = conectar_db()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            DELETE FROM detalle_carrito WHERE id = %s
        """, (id_detalle,))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al eliminar producto del carrito:", e)
        return False

def actualizar_cantidad(id_detalle, nueva_cantidad):
    conexion = conectar_db()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE detalle_carrito
            SET cantidad = %s
            WHERE id = %s
        """, (nueva_cantidad, id_detalle))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al actualizar cantidad:", e)
        return False

 
def validar_stock_carrito(id_carrito):
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    query = """
        SELECT dc.id, dc.cantidad, p.stock, p.nombre
        FROM detalle_carrito dc
        JOIN productos p ON dc.id_producto = p.id
        WHERE dc.id_carrito = %s
    """
    cursor.execute(query, (id_carrito,))
    resultados = cursor.fetchall()
    conexion.close()

    errores = []
    for fila in resultados:
        if fila[1] > fila[2]:  # cantidad > stock
            errores.append({
                "producto": fila[3],
                "stock_disponible": fila[2],
                "cantidad_solicitada": fila[1]
            })

    return errores  # ✅ SOLO retorna lista


def descontar_stock_carrito(id_carrito):
    conexion = conectar_db()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()

        # Obtener productos y cantidades del carrito
        cursor.execute("""
            SELECT id_producto, cantidad
            FROM detalle_carrito
            WHERE id_carrito = %s
        """, (id_carrito,))
        productos = cursor.fetchall()

        for producto in productos:
            id_producto, cantidad = producto
            cursor.execute("""
                UPDATE productos
                SET stock = stock - %s
                WHERE id = %s
            """, (cantidad, id_producto))

        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al descontar stock:", e)
        return False

def obtener_total_carrito(id_carrito):
    conexion = conectar_db()
    if conexion is None:
        return 0.0

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT SUM(dc.cantidad * dc.precio_unitario)
            FROM detalle_carrito dc
            WHERE dc.id_carrito = %s
        """, (id_carrito,))
        total = cursor.fetchone()[0]
        conexion.close()
        return float(total) if total else 0.0
    except Exception as e:
        print("❌ Error al obtener total del carrito:", e)
        return 0.0

#Antes de agregar un producto, verifica si ya está para sumar cantidades:
def producto_en_carrito(id_carrito, id_producto):
    conexion = conectar_db()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, cantidad
            FROM detalle_carrito
            WHERE id_carrito = %s AND id_producto = %s
        """, (id_carrito, id_producto))
        resultado = cursor.fetchone()
        conexion.close()
        return resultado  # None o (id, cantidad)
    except Exception as e:
        print("❌ Error al verificar producto:", e)
        return False

def vaciar_carrito(id_carrito):
    conexion = conectar_db()
    if conexion is None:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM detalle_carrito WHERE id_carrito = %s", (id_carrito,))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al vaciar carrito:", e)
        return False

def contar_productos_en_carrito(id_carrito):
    conexion = conectar_db()
    if conexion is None:
        return 0
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM detalle_carrito WHERE id_carrito = %s
        """, (id_carrito,))
        cantidad = cursor.fetchone()[0]
        conexion.close()
        return cantidad
    except Exception as e:
        print("❌ Error al contar productos:", e)
        return 0

def calcular_total_productos(id_carrito):
    conexion = conectar_db()
    if conexion is None:
        return 0.0

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT SUM(cantidad * precio_unitario)
            FROM detalle_carrito
            WHERE id_carrito = %s
        """, (id_carrito,))
        resultado = cursor.fetchone()
        conexion.close()
        return float(resultado[0]) if resultado[0] else 0.0
    except Exception as e:
        print("❌ Error al calcular total bruto:", e)
        return 0.0
    







    # ✅ Al final del archivo models/detalle_carrito.py



#esto solo sirve para la voz no para nada mas
def eliminar_producto_de_carrito(id_carrito, id_producto):
    conexion = conectar_db()
    if conexion is None:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            DELETE FROM detalle_carrito
            WHERE id_carrito = %s AND id_producto = %s
        """, (id_carrito, id_producto))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al eliminar producto del carrito:", e)
        return False





#ia 
def listar_productos_carrito_para_ia(id_carrito):
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT dc.id_producto
            FROM detalle_carrito dc
            WHERE dc.id_carrito = %s
        """, (id_carrito,))
        filas = cursor.fetchall()
        conexion.close()
        return [{"id_producto": f[0]} for f in filas]
    except Exception as e:
        print("❌ Error al listar productos IA:", e)
        return []
