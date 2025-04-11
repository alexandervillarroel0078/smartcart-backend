from config import conectar_db

# Obtener todos los productos con su categoría
def obtener_productos():
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        cursor.execute("""
    SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock, p.umbral_minimo, c.nombre AS categoria
    FROM productos p
    JOIN categorias c ON p.id_categoria = c.id
""")


        productos = cursor.fetchall()
        conexion.close()

        resultado = []
        for fila in productos:
            resultado.append({
                "id": fila[0],
                "nombre": fila[1],
                "descripcion": fila[2],
                "precio": float(fila[3]),
                "stock": fila[4],
                 "umbral_stock": fila[5],  # ✅ esto debe estar
                "categoria": fila[6]
            })
        return resultado
    except Exception as e:
        print("❌ Error al obtener productos:", e)
        return []

def registrar_producto(nombre, descripcion, precio, stock, umbral_stock, id_categoria, imagen):
    conexion = conectar_db()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, descripcion, precio, stock, umbral_stock, id_categoria, imagen)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, descripcion, precio, stock, umbral_stock, id_categoria, imagen))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al registrar producto:", e)
        return False

#################################
def editar_producto(id, nombre, descripcion, precio, stock, umbral_stock, id_categoria):
    conexion = conectar_db()
    if conexion is None:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE productos
            SET nombre = %s,
                descripcion = %s,
                precio = %s,
                stock = %s,
                umbral_stock = %s,
                id_categoria = %s
            WHERE id = %s
        """, (nombre, descripcion, precio, stock, umbral_stock, id_categoria, id))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al editar producto:", e)
        return False


#################################
def eliminar_producto(id):
    conexion = conectar_db()
    if conexion is None:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al eliminar producto:", e)
        return False

# ✅ Dirección: models/producto.py

def sumar_stock_producto(id_producto, cantidad):
    conexion = conectar_db()
    if conexion is None:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE productos
            SET stock = stock + %s
            WHERE id = %s
        """, (cantidad, id_producto))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al sumar stock:", e)
        return False



def obtener_productos_paginados(pagina=1, por_pagina=10):
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        offset = (pagina - 1) * por_pagina
        cursor.execute("""
            SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock, p.umbral_stock,
                   c.nombre AS categoria, p.visible, p.imagen
            FROM productos p
            JOIN categorias c ON p.id_categoria = c.id
            ORDER BY p.nombre
            LIMIT %s OFFSET %s
        """, (por_pagina, offset))
        productos = cursor.fetchall()
        conexion.close()

        return [
            {
                "id": p[0],
                "nombre": p[1],
                "descripcion": p[2],
                "precio": float(p[3]),
                "stock": p[4],
                "umbral_stock": p[5],
                "categoria": p[6],
                "visible": p[7],
                "imagen": p[8],
            }
            for p in productos
        ]
    except Exception as e:
        print("❌ Error al obtener productos paginados:", e)
        return []


 
def obtener_productos_catalogo():
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock, p.imagen,
                   p.id_categoria, c.nombre AS categoria
            FROM productos p
            JOIN categorias c ON p.id_categoria = c.id
            WHERE p.visible = TRUE
            ORDER BY p.nombre
        """)
        productos = cursor.fetchall()
        conexion.close()

        return [
            {
                "id": p[0],
                "nombre": p[1],
                "descripcion": p[2],
                "precio": float(p[3]),
                "stock": p[4],
                "imagen": p[5],
                "id_categoria": p[6],
                "categoria": p[7],
                "visible": True
            }
            for p in productos
        ]
    except Exception as e:
        print("❌ Error al obtener productos del catálogo:", e)
        return []
