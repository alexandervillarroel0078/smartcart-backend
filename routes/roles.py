from flask import Blueprint, jsonify, request,g
from models.roles import obtener_roles, crear_rol, actualizar_rol, eliminar_rol
from utils.token import token_requerido

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/roles', methods=['GET'])
@token_requerido
def listar_roles():
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403
    roles = obtener_roles()
    return jsonify({"roles": roles})


@roles_bp.route('/roles', methods=['POST'])
@token_requerido
def crear():
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403
    data = request.get_json()
    if not data or 'nombre' not in data:
        return jsonify({"mensaje": "Nombre del rol requerido"}), 400
    if crear_rol(data['nombre']):
        return jsonify({"mensaje": "Rol creado exitosamente"}), 201
    return jsonify({"mensaje": "Error al crear rol"}), 500


@roles_bp.route('/roles/<int:id>', methods=['PUT'])
@token_requerido
def actualizar(id):
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403
    data = request.get_json()
    if not data or 'nombre' not in data:
        return jsonify({"mensaje": "Nombre requerido"}), 400
    if actualizar_rol(id, data['nombre']):
        return jsonify({"mensaje": "Rol actualizado"})
    return jsonify({"mensaje": "Error al actualizar rol"}), 500


@roles_bp.route('/roles/<int:id>', methods=['DELETE'])
@token_requerido
def eliminar(id):
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403
    if eliminar_rol(id):
        return jsonify({"mensaje": "Rol eliminado"})
    return jsonify({"mensaje": "Error al eliminar rol"}), 500
