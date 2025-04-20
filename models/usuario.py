# models/usuario.py
import random
import string
import psycopg2
from config import conectar_db
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
# Obtener todos los usuarios

def obtener_usuarios():
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT u.id, u.nombre, u.correo, r.nombre FROM usuarios u JOIN roles r ON u.id_rol = r.id")
        filas = cursor.fetchall()
        conexion.close()

        # Convertir listas a diccionarios
        usuarios = [
            {
                "id": fila[0],
                "nombre": fila[1],
                "correo": fila[2],
                "rol": fila[3]
            }
            for fila in filas
        ]
        return usuarios
    except Exception as e:
        print("❌ Error al obtener usuarios:", e)
        return []

def registrar_usuario(nombre, correo, password, id_rol):
    conexion = conectar_db()
    if conexion is None:
        return None

    try:
        password_hash = generate_password_hash(password)
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, password, id_rol)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (nombre, correo, password_hash, id_rol))
        nuevo_id = cursor.fetchone()[0]
        conexion.commit()
        conexion.close()
        return nuevo_id  # ← Esto es importante
    except Exception as e:
        print("❌ Error al registrar usuario:", e)
        return None



    #login

def login_usuario(correo, password):
    conexion = conectar_db()
    if conexion is None:
        return None

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT u.id, u.nombre, u.correo, u.password, r.nombre
            FROM usuarios u
            JOIN roles r ON u.id_rol = r.id
            WHERE u.correo = %s
        """, (correo,))
        usuario = cursor.fetchone()
        conexion.close()

        if usuario and check_password_hash(usuario[3], password):
            return {
                "id": usuario[0],
                "nombre": usuario[1],
                "correo": usuario[2],
                "rol": usuario[4]
            }
        else:
            return None
    except Exception as e:
        print("❌ Error en login:", e)
        return None
    
def editar_usuario(id_usuario, nombre, correo, id_rol):
    conexion = conectar_db()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE usuarios
            SET nombre = %s, correo = %s, id_rol = %s
            WHERE id = %s
        """, (nombre, correo, id_rol, id_usuario))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al editar usuario:", e)
        return False

def eliminar_usuario(id_usuario):
    conexion = conectar_db()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id_usuario,))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al eliminar usuario:", e)
        return False

def definir_nombre_aleatorio():
    nombres = ["Explorador", "Visitante", "Cliente", "Comprador", "Invitado"]
    return random.choice(nombres) + str(random.randint(1000, 9999))

def registrar_visitante(intentos=5):
    conexion = conectar_db()
    if conexion is None:
        raise Exception("No se pudo conectar a la base de datos")

    try:
        cursor = conexion.cursor()
        for _ in range(intentos):
            nombre = definir_nombre_aleatorio()
            correo = f"{nombre.lower()}@visitante.com"
            id_rol_cliente = 3  # Asegúrate que el rol cliente tenga ID 3

            try:
                cursor.execute("""
                    INSERT INTO usuarios (nombre, correo, id_rol)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (nombre, correo, id_rol_cliente))
                id_nuevo = cursor.fetchone()[0]
                conexion.commit()
                conexion.close()
                return id_nuevo
            except psycopg2.errors.UniqueViolation:
                conexion.rollback()  # 👈 Importante para seguir en el siguiente intento
                continue  # Intentar con otro nombre aleatorio

        raise Exception("❌ No se pudo registrar un visitante único después de varios intentos")

    except Exception as e:
        print("❌ Error al registrar visitante:", e)
        raise e









