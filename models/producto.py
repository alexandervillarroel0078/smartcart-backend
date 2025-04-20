
#Dirección: models/producto.py
from config import conectar_db
from word2number import w2n
def obtener_productos():
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock,
                   p.umbral_minimo, p.umbral_maximo, p.modelo, c.nombre AS categoria
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
                "umbral_minimo": fila[5],
                "umbral_maximo": fila[6],
                "modelo": fila[7],
                "categoria": fila[8]
            })
        return resultado
    except Exception as e:
        print("❌ Error al obtener productos:", e)
        return []


def registrar_producto(nombre, descripcion, precio, stock, umbral_minimo, umbral_maximo, modelo, id_categoria, imagen, visible=True):
    conexion = conectar_db()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO productos (
                nombre, descripcion, precio, stock, umbral_minimo,
                umbral_maximo, modelo, id_categoria, imagen, visible
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            nombre, descripcion, precio, stock,
            umbral_minimo, umbral_maximo, modelo,
            id_categoria, imagen, visible
        ))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al registrar producto:", e)
        return False



def editar_producto(id, nombre, descripcion, precio, stock, umbral_minimo, umbral_maximo, modelo, id_categoria):
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
                umbral_minimo = %s,
                umbral_maximo = %s,
                modelo = %s,
                id_categoria = %s
            WHERE id = %s
        """, (nombre, descripcion, precio, stock, umbral_minimo, umbral_maximo, modelo, id_categoria, id))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al editar producto:", e)
        return False


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


def obtener_productos_paginados(pagina=1, por_pagina=10):
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        offset = (pagina - 1) * por_pagina
        cursor.execute("""
            SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock,
                   p.umbral_minimo, p.umbral_maximo, p.modelo,
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
                "umbral_minimo": p[5],
                "umbral_maximo": p[6],
                "modelo": p[7],
                "categoria": p[8],
                "visible": p[9],
                "imagen": p[10],
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
                   p.id_categoria, c.nombre AS categoria,
                   p.modelo, p.umbral_minimo, p.umbral_maximo
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
                "modelo": p[8],
                "umbral_minimo": p[9],
                "umbral_maximo": p[10],
                "visible": True
            }
            for p in productos
        ]
    except Exception as e:
        print("❌ Error al obtener productos del catálogo:", e)
        return []


def registrar_entrada_stock(id_producto, cantidad, id_usuario=None, observacion=None):
    conexion = conectar_db()
    if conexion is None:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO entradas_stock (id_producto, cantidad, id_usuario, observacion)
            VALUES (%s, %s, %s, %s)
        """, (id_producto, cantidad, id_usuario, observacion))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al registrar entrada de stock:", e)
        return False


def sumar_stock_producto(id_producto, cantidad, id_usuario=None, observacion=None):
    conexion = conectar_db()
    if conexion is None:
        return False
    try:
        cursor = conexion.cursor()

        # Actualizar stock
        cursor.execute("""
            UPDATE productos
            SET stock = stock + %s
            WHERE id = %s
        """, (cantidad, id_producto))

        # Registrar entrada en historial (mismo cursor)
        cursor.execute("""
            INSERT INTO entradas_stock (id_producto, cantidad, id_usuario, observacion)
            VALUES (%s, %s, %s, %s)
        """, (id_producto, cantidad, id_usuario, observacion))

        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al sumar stock o registrar entrada:", e)
        return False


def obtener_historial_entradas_stock():
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT es.id, p.nombre AS producto, es.cantidad, u.nombre AS usuario,
                   es.observacion, es.fecha
            FROM entradas_stock es
            JOIN productos p ON es.id_producto = p.id
            LEFT JOIN usuarios u ON es.id_usuario = u.id
            ORDER BY es.fecha DESC
        """)
        historial = cursor.fetchall()
        conexion.close()

        return [
            {
                "id": fila[0],
                "producto": fila[1],
                "cantidad": fila[2],
                "usuario": fila[3] if fila[3] else "Desconocido",
                "observacion": fila[4],
                "fecha": fila[5].strftime('%Y-%m-%d %H:%M')
            }
            for fila in historial
        ]
    except Exception as e:
        print("❌ Error al obtener historial de entradas:", e)
        return []


# funciones para exlusivos para la voz
#Dirección: models/producto.py
import difflib
import unicodedata
# 🔤 Función auxiliar para normalizar texto
def normalizar(texto):
    texto = texto.lower().strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn')
    return texto

# ✅ Función mejorada para obtener producto por nombre con similitud

def obtener_producto_por_nombre(nombre_voz):
    conexion = conectar_db()
    if conexion is None:
        return None

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, nombre, descripcion, precio
            FROM productos
           
        """)
        productos = cursor.fetchall()
        conexion.close()

        nombre_voz_normalizado = normalizar(nombre_voz)
        nombres_db = [normalizar(p[1]) for p in productos]
        print("🎤 Nombre voz normalizado:", nombre_voz_normalizado)
        print("📦 Productos normalizados:", nombres_db)

        # Buscar el nombre más parecido al dicho por voz
        coincidencias = difflib.get_close_matches(nombre_voz_normalizado, nombres_db, n=1, cutoff=0.3)

        if coincidencias:
            nombre_encontrado = coincidencias[0]
            for p in productos:
                if normalizar(p[1]) == nombre_encontrado:
                    print("🔍 Texto normalizado:", nombre_voz_normalizado)
                    print("📚 Comparando contra:", nombres_db)
                    print("🎯 Coincidencia:", coincidencias)

                    return {
                        "id": p[0],
                        "nombre": p[1],
                        "descripcion": p[2],
                        "precio": float(p[3])
                    }

        
            print("⚠️ No se encontró coincidencia para:", nombre_voz_normalizado)
            return None     
    except Exception as e:
        print("❌ Error al buscar producto por similitud:", e)
        return None



def obtener_producto_por_id(id_producto):
    conexion = conectar_db()
    if conexion is None:
        return None

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, nombre, descripcion, precio, stock, imagen
            FROM productos
            WHERE id = %s
        """, (id_producto,))
        fila = cursor.fetchone()
        conexion.close()

        if fila:
            return {
                "id": fila[0],
                "nombre": fila[1],
                "descripcion": fila[2],
                "precio": float(fila[3]),
                "stock": fila[4],
                "imagen": fila[5]
            }
        return None
    except Exception as e:
        print("❌ Error al obtener producto por ID:", e)
        return None
