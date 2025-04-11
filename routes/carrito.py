# routes/carrito.py
from flask import Blueprint, request, jsonify
from models.carrito import obtener_carrito_activo, crear_carrito, cerrar_carrito
from models.bitacora import registrar_bitacora
from utils.token import token_requerido

carrito_bp = Blueprint('carrito', __name__)

# 📌 Crear carrito si no existe
@carrito_bp.route('/carrito/crear', methods=['POST'])
@token_requerido
def crear_carrito_si_no_existe():
    if request.usuario['rol'] not in ['cliente', 'cajero']:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    id_usuario = request.usuario['id']
    carrito_id = obtener_carrito_activo(id_usuario)

    if carrito_id:
        return jsonify({"mensaje": "Ya tienes un carrito activo", "id_carrito": carrito_id})
    
    nuevo_id = crear_carrito(id_usuario)
    if nuevo_id:
        registrar_bitacora(id_usuario, "Creó un nuevo carrito", request.remote_addr)
        return jsonify({"mensaje": "Carrito creado", "id_carrito": nuevo_id})
    else:
        return jsonify({"mensaje": "Error al crear carrito"}), 500

# 📌 Ver ID de carrito activo
@carrito_bp.route('/carrito/ver', methods=['GET'])
@token_requerido
def ver_carrito_id():
    id_usuario = request.usuario['id']
    id_carrito = obtener_carrito_activo(id_usuario)
    if not id_carrito:
        return jsonify({"mensaje": "No tienes un carrito activo"}), 404
    return jsonify({"id_carrito": id_carrito})

# 📌 (opcional) Cerrar carrito directamente (para pruebas)
@carrito_bp.route('/carrito/cerrar/<int:id_carrito>', methods=['POST'])
@token_requerido
def cerrar_carrito_ruta(id_carrito):
    if cerrar_carrito(id_carrito):
        registrar_bitacora(request.usuario['id'], f"Cerró carrito ID {id_carrito}", request.remote_addr)
        return jsonify({"mensaje": "Carrito cerrado exitosamente"})
    else:
        return jsonify({"mensaje": "Error al cerrar carrito"}), 500
