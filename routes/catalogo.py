from flask import Blueprint, jsonify
from config import conectar_db
from utils.token import token_requerido

catalogo_bp = Blueprint('catalogo', __name__)

@catalogo_bp.route('/catalogo', methods=['GET'])
@token_requerido
def ver_catalogo_publico():
    conexion = conectar_db()
    if conexion is None:
        return jsonify({"mensaje": "Error de conexión"}), 500

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock, c.nombre AS categoria, p.imagen
            FROM productos p
            JOIN categorias c ON p.id_categoria = c.id
            WHERE p.visible = TRUE
            ORDER BY p.nombre
        """)
        productos = cursor.fetchall()
        conexion.close()

        return jsonify([
            {
                "id": p[0],
                "nombre": p[1],
                "descripcion": p[2],
                "precio": float(p[3]),
                "stock": p[4],
                "categoria": p[5],
                "estado": "Agotado" if p[4] == 0 else "Disponible",
                "imagen": p[6]  # Asegúrate de que tu tabla tenga esta columna
            }
            for p in productos
        ])
    except Exception as e:
        print("❌ Error al obtener catálogo:", e)
        return jsonify({"mensaje": "Error interno"}), 500
