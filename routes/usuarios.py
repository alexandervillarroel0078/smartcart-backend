from flask import Blueprint, request, jsonify, g
from models.usuario import obtener_usuarios, registrar_usuario
from models.bitacora import registrar_bitacora
from utils.token import token_requerido
from models.usuario import (
    obtener_usuarios,
    registrar_usuario,
    editar_usuario,
    eliminar_usuario
)
from models.usuario import eliminar_usuario
usuarios_bp = Blueprint('usuarios', __name__)
from config import conectar_db  # <-- Agregalo si no está


@usuarios_bp.route('/usuarios')
@token_requerido
def listar_usuarios():
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    usuarios = obtener_usuarios()
    return {'usuarios': usuarios}

@usuarios_bp.route('/usuarios/<int:id>', methods=['GET'])
@token_requerido
def obtener_usuario_por_id(id):
    conexion = conectar_db()
    if conexion is None:
        return jsonify({"mensaje": "Error de conexión"}), 500

    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, correo, id_rol FROM usuarios WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        conexion.close()

        if usuario:
            return jsonify({
                "id": usuario[0],
                "nombre": usuario[1],
                "correo": usuario[2],
                "id_rol": usuario[3]
            })
        else:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404
    except Exception as e:
        print("❌ Error al obtener usuario por ID:", e)
        return jsonify({"mensaje": "Error interno"}), 500


@usuarios_bp.route('/usuarios/agregar', methods=['POST'])
@token_requerido
def agregar_usuario():    
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403
    datos = request.get_json()
    nombre = datos.get('nombre')
    correo = datos.get('correo')
    password = datos.get('password')
    id_rol = datos.get('id_rol')
    exito = registrar_usuario(nombre, correo, password, id_rol)
    if exito and id_rol == 4:  # Suponiendo que id_rol 4 = cliente
        from models.clientes import registrar_cliente
        registrar_cliente(exito)  # exito contiene el ID del nuevo usuario
    if exito:
        registrar_bitacora(
            id_usuario=g.usuario['id'],
            accion=f"Registró nuevo usuario: {nombre}",
            ip=request.remote_addr
        )
        return jsonify({"success": True, "mensaje": "Usuario registrado correctamente"})
    else:
        return jsonify({"success": False, "mensaje": "Error al registrar usuario"}), 500
    
@usuarios_bp.route('/usuarios/<int:id>', methods=['PUT'])
@token_requerido
def actualizar_usuario(id):
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    datos = request.get_json()
    nombre = datos.get('nombre')
    correo = datos.get('correo')
    id_rol = datos.get('id_rol')

    exito = editar_usuario(id, nombre, correo, id_rol)
    if exito:
        registrar_bitacora(
            id_usuario=g.usuario['id'],
            accion=f"Editó usuario ID {id}",
            ip=request.remote_addr
        )
        return jsonify({"success": True, "mensaje": "Usuario actualizado"})
    else:
        return jsonify({"success": False, "mensaje": "Error al actualizar usuario"}), 500

@usuarios_bp.route('/usuarios/<int:id>', methods=['DELETE'])
@token_requerido
def borrar_usuario(id):
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    exito = eliminar_usuario(id)
    if exito:
        registrar_bitacora(
            id_usuario=g.usuario['id'],
            accion=f"Eliminó usuario ID {id}",
            ip=request.remote_addr
        )
        return jsonify({"success": True, "mensaje": "Usuario eliminado"})
    else:
        return jsonify({"success": False, "mensaje": "Error al eliminar usuario"}), 500





 