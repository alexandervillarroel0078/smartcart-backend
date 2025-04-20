# routes/detalle_carrito.py
from flask import Blueprint, request, jsonify,g
from models.detalle_carrito import (
    listar_productos_carrito,
    eliminar_producto,
    agregar_producto,
    actualizar_cantidad,
    obtener_total_carrito,
    obtener_total_carrito,
    vaciar_carrito,validar_stock_carrito
)
from models.carrito import obtener_carrito_activo
from models.bitacora import registrar_bitacora
from utils.token import token_requerido

detalle_carrito_bp = Blueprint('detalle_carrito', __name__)
# 📌 Agregar producto al carrito
@detalle_carrito_bp.route('/detalle_carrito/agregar', methods=['POST'])
@token_requerido
def agregar_producto_detalle():
    if g.usuario['rol'] not in ['cliente', 'cajero']:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    datos = request.get_json()
    id_usuario = g.usuario['id']
    id_producto = datos.get('id_producto')
    cantidad = datos.get('cantidad')
    precio_unitario = datos.get('precio_unitario')

    id_carrito = obtener_carrito_activo(id_usuario)
    if not id_carrito:
        return jsonify({"mensaje": "No tienes un carrito activo"}), 400

    exito = agregar_producto(id_carrito, id_producto, cantidad, precio_unitario)
    if exito:
        registrar_bitacora(id_usuario, f"Agregó producto ID {id_producto} al carrito", request.remote_addr)
        return jsonify({"success": True, "mensaje": "Producto agregado al carrito"})
    else:
        return jsonify({"success": False, "mensaje": "Error al agregar producto"}), 500


# 📌 Ver productos en el carrito activo
@detalle_carrito_bp.route('/detalle_carrito/ver', methods=['GET'])
@token_requerido
def ver_detalle_carrito():
    id_usuario = g.usuario['id']
    id_carrito = obtener_carrito_activo(id_usuario)

    if not id_carrito:
        return jsonify({"mensaje": "No tienes un carrito activo"}), 404

    productos = listar_productos_carrito(id_carrito)
    return jsonify({"detalle_carrito": productos})


# 📌 Actualizar cantidad de un producto del carrito (opcional pero pro)
@detalle_carrito_bp.route('/detalle_carrito/actualizar/<int:id_detalle>', methods=['PUT'])
@token_requerido
def actualizar_producto_detalle(id_detalle):
    if g.usuario['rol'] not in ['cliente', 'cajero']:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    datos = request.get_json()
    nueva_cantidad = datos.get('cantidad')

    exito = actualizar_cantidad(id_detalle, nueva_cantidad)
    if exito:
        registrar_bitacora(g.usuario['id'], f"Actualizó cantidad del producto detalle ID {id_detalle} a {nueva_cantidad}", request.remote_addr)
        return jsonify({"success": True, "mensaje": "Cantidad actualizada"})
    else:
        return jsonify({"success": False, "mensaje": "Error al actualizar cantidad"}), 500


# 📌 Eliminar producto del carrito
@detalle_carrito_bp.route('/detalle_carrito/eliminar/<int:id_detalle>', methods=['DELETE'])
@token_requerido
def eliminar_producto_detalle(id_detalle):
    if g.usuario['rol'] not in ['cliente', 'cajero']:
        return jsonify({"mensaje": "Acceso denegado"}), 403
    exito = eliminar_producto(id_detalle)
    if exito:
        registrar_bitacora(g.usuario['id'], f"Eliminó un producto del detalle del carrito (ID {id_detalle})", request.remote_addr)
        return jsonify({"success": True, "mensaje": "Producto eliminado del carrito"})
    else:
        return jsonify({"success": False, "mensaje": "Error al eliminar producto"}), 500
    

@detalle_carrito_bp.route('/detalle_carrito/total', methods=['GET'])
@token_requerido
def ver_total_carrito():
    id_usuario = g.usuario['id']
    id_carrito = obtener_carrito_activo(id_usuario)    
    if not id_carrito:
        return jsonify({"mensaje": "No tienes un carrito activo"}), 404
    
    total = obtener_total_carrito(id_carrito)
    return jsonify({"total": total})


@detalle_carrito_bp.route('/detalle_carrito/vaciar', methods=['DELETE'])
@token_requerido
def vaciar_carrito_ruta():
    id_usuario = g.usuario['id']
    id_carrito = obtener_carrito_activo(id_usuario)

    if not id_carrito:
        return jsonify({"mensaje": "No tienes un carrito activo"}), 404

    if vaciar_carrito(id_carrito):
        registrar_bitacora(id_usuario, f"Vació todo el carrito ID {id_carrito}", request.remote_addr)
        return jsonify({"success": True, "mensaje": "Carrito vaciado correctamente"})
    else:
        return jsonify({"success": False, "mensaje": "Error al vaciar carrito"}), 500


@detalle_carrito_bp.route("/detalle_carrito/validar", methods=["GET"])
@token_requerido
def validar_stock():
    id_usuario = g.usuario["id"]
    # Suponemos que el carrito activo es único por usuario
    from models.carrito import obtener_carrito_activo
    id_carrito = obtener_carrito_activo(id_usuario)

    errores = validar_stock_carrito(id_carrito)
    if errores:
        return jsonify({"success": False, "problemas": errores}), 400
    return jsonify({"success": True})

