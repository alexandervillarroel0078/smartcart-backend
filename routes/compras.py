# 📁 routes/compras.py
from flask import Blueprint, jsonify
from models.compra import obtener_detalle_compra

compras_bp = Blueprint('compras', __name__)

@compras_bp.route('/compras/<int:id_compra>', methods=['GET'])
def ver_detalle_compra(id_compra):
    detalle = obtener_detalle_compra(id_compra)
    if detalle:
        return jsonify(detalle), 200
    else:
        return jsonify({"error": "Compra no encontrada"}), 404
