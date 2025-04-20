# 📁 routes/reportes.py
from flask import Blueprint, request, jsonify
from utils.token import token_requerido
from config import conectar_db

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/reportes/compras', methods=['GET'])
@token_requerido
def listar_compras():
    # Solo administrador puede ver todas las compras
    from flask import g
    if g.usuario['rol'] != 'administrador':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT c.id, u.nombre, c.total, c.fecha
                FROM compras c
                JOIN usuarios u ON c.id_cliente = u.id
                ORDER BY c.fecha DESC
            """)
            compras = cursor.fetchall()
            conexion.close()
            return jsonify([
                {
                    "id": fila[0],
                    "cliente": fila[1],
                    "total": float(fila[2]),
                    "fecha": fila[3].strftime("%Y-%m-%d %H:%M")
                }
                for fila in compras
            ])
        except Exception as e:
            print("❌ Error al listar compras:", e)
            return jsonify({"mensaje": "Error al obtener compras"}), 500
