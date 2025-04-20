from config import conectar_db

def obtener_roles():
    conexion = conectar_db()
    if conexion is None:
        return []
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre FROM roles")
        filas = cursor.fetchall()
        conexion.close()
        return [{"id": r[0], "nombre": r[1]} for r in filas]
    except Exception as e:
        print("❌ Error al obtener roles:", e)
        return []

def crear_rol(nombre):
    conexion = conectar_db()
    try:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO roles (nombre) VALUES (%s)", (nombre,))
        conexion.commit()
        return True
    except Exception as e:
        print("❌ Error al crear rol:", e)
        return False

def actualizar_rol(id, nombre):
    conexion = conectar_db()
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE roles SET nombre = %s WHERE id = %s", (nombre, id))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("❌ Error al actualizar rol:", e)
        return False

def eliminar_rol(id):
    conexion = conectar_db()
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM roles WHERE id = %s", (id,))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("❌ Error al eliminar rol:", e)
        return False
