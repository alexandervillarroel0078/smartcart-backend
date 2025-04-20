from flask import Blueprint, request, jsonify,g
from models.clientes import listar_clientes, obtener_historial_compras, obtener_reporte_cliente
from utils.token import token_requerido

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/clientes', methods=['GET'])
@token_requerido
def obtener_clientes():
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403
    clientes = listar_clientes()
    return jsonify({"clientes": clientes})

@clientes_bp.route('/clientes/<int:id>/historial', methods=['GET'])
@token_requerido
def historial_cliente(id):
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403
    historial = obtener_historial_compras(id)
    return jsonify({"historial": historial})

@clientes_bp.route('/clientes/<int:id>/reporte', methods=['GET'])
@token_requerido
def reporte_cliente(id):
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403
    reporte = obtener_reporte_cliente(id)
    return jsonify({"reporte": reporte})

