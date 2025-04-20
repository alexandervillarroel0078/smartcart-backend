from config import conectar_db

def obtener_categorias():
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre FROM categorias")
        categorias = cursor.fetchall()
        conexion.close()

        return [{"id": c[0], "nombre": c[1]} for c in categorias]
    except Exception as e:
        print("❌ Error al obtener categorías:", e)
        return []
