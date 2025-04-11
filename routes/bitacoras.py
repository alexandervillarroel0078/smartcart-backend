from flask import Blueprint, jsonify, request
from models.bitacora import obtener_bitacora
from utils.token import token_requerido

bitacora_bp = Blueprint('bitacora', __name__)

@bitacora_bp.route('/bitacora')
@token_requerido
def listar_bitacora():
    if request.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    bitacora = obtener_bitacora()
    return {'bitacora': bitacora}
