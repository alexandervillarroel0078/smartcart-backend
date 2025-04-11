from flask import Blueprint,request, jsonify
from utils.token import token_requerido
from models.reportes import obtener_reporte_cliente
from models.reportes import obtener_reporte_por_cliente
reportes_bp = Blueprint("reportes", __name__)

@reportes_bp.route('/reportes/cliente/<int:id_cliente>', methods=['GET'])
@token_requerido
def generar_reporte(id_cliente):
    if request.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403
    reporte = obtener_reporte_cliente(id_cliente)
    if reporte:
        return jsonify(reporte), 200
    else:
        return jsonify({"mensaje": "Error al generar reporte"}), 500


@reportes_bp.route('/reportes/cliente/<int:id_cliente>', methods=['GET'])
@token_requerido
def reporte_cliente(id_cliente):
    compras = obtener_reporte_por_cliente(id_cliente)    
    if compras is None:
        return jsonify({"mensaje": "Error al generar reporte"}), 500

    return jsonify({
        "cliente_id": id_cliente,
        "compras": compras
    })