from config import conectar_db

def guardar_calificacion(id_compra, puntuacion):
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO calificaciones (id_compra,calificacion)
            VALUES (%s, %s)
        """, (id_compra, puntuacion))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al guardar calificación:", e)
        return False
