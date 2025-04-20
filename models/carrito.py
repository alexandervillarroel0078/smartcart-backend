# models/carrito.py
from config import conectar_db

def obtener_carrito_activo(id_usuario):
    conexion = conectar_db()
    if conexion is None:
        return None

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id FROM carrito 
            WHERE id_usuario = %s AND estado = 'activo'
            ORDER BY fecha DESC LIMIT 1
        """, (id_usuario,))
        carrito = cursor.fetchone()
        conexion.close()
        return carrito[0] if carrito else None
    except Exception as e:
        print("❌ Error al obtener carrito activo:", e)
        return None

def crear_carrito(id_usuario):
    conexion = conectar_db()
    if conexion is None:
        return None

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO carrito (id_usuario) VALUES (%s) RETURNING id
        """, (id_usuario,))
        id_nuevo = cursor.fetchone()[0]
        conexion.commit()
        conexion.close()
        return id_nuevo
    except Exception as e:
        print("❌ Error al crear carrito:", e)
        return None

def cerrar_carrito(id_carrito):
    conexion = conectar_db()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE carrito SET estado = 'cerrado' WHERE id = %s
        """, (id_carrito,))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al cerrar carrito:", e)
        return False

def cerrar_carritos_abiertos(id_usuario):
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE carrito
                SET estado = 'cerrado'
                WHERE id_usuario = %s AND estado = 'activo'
            """, (id_usuario,))
            conexion.commit()
            conexion.close()
            return True
        except Exception as e:
            print("❌ Error al cerrar carritos antiguos:", e)
    return False
 