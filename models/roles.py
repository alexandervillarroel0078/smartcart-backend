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
