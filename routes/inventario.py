# routes/inventario.py
from flask import Blueprint, request, jsonify
from models.inventario import registrar_movimiento_inventario, obtener_alertas_bajo_stock
from utils.token import token_requerido

inventario_bp = Blueprint('inventario', __name__)

# Ruta para registrar entrada o salida de inventario
@inventario_bp.route('/inventario/movimiento', methods=['POST'])
@token_requerido
def registrar_movimiento():
    if request.usuario['rol'] not in ['almacenero', 'admin']:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    datos = request.get_json()
    id_producto = datos.get('id_producto')
    tipo = datos.get('tipo')  # 'entrada' o 'salida'
    cantidad = datos.get('cantidad')
    motivo = datos.get('motivo')

    exito = registrar_movimiento_inventario(id_producto, tipo, cantidad, motivo)
    if exito:
        return jsonify({"success": True, "mensaje": "Movimiento registrado correctamente"})
    else:
        return jsonify({"success": False, "mensaje": "Error al registrar movimiento"}), 500

# Ruta para obtener productos con bajo stock
@inventario_bp.route('/inventario/alertas', methods=['GET'])
@token_requerido
def alertas_bajo_stock():
    if request.usuario['rol'] not in ['almacenero', 'admin']:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    alertas = obtener_alertas_bajo_stock()
    return jsonify({"alertas": alertas})
