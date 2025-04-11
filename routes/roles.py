from flask import Blueprint, jsonify, request
from models.roles import obtener_roles
from utils.token import token_requerido

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/roles', methods=['GET'])
@token_requerido
def listar_roles():
    if request.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    roles = obtener_roles()
    return jsonify({"roles": roles})
