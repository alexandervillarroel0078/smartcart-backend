from config import conectar_db

def registrar_bitacora(id_usuario, accion, ip):
    conexion = conectar_db()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO bitacora (id_usuario, accion, ip)
            VALUES (%s, %s, %s)
        """, (id_usuario, accion, ip))
        conexion.commit()
        conexion.close()
        print(f"📝 Bitácora: {accion} (usuario {id_usuario})")
    except Exception as e:
        print("❌ Error al registrar bitácora:", e)

def obtener_bitacora():
    conexion = conectar_db()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT b.id, u.nombre, b.accion, b.fecha_hora, b.ip
            FROM bitacora b
            JOIN usuarios u ON b.id_usuario = u.id
            ORDER BY b.fecha_hora DESC
        """)
        registros = cursor.fetchall()
        conexion.close()
        return [
            {
                "id": r[0],
                "usuario": r[1],
                "accion": r[2],
                "fecha_hora": r[3],
                "ip": r[4]
            } for r in registros
        ]
    except Exception as e:
        print("❌ Error al obtener bitácora:", e)
        return []