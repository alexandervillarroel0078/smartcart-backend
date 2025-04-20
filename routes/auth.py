from flask import Blueprint, request, jsonify
from models.usuario import login_usuario
from models.usuario import registrar_visitante

from models.bitacora import registrar_bitacora
import jwt
import datetime
from flask import current_app as app
from config import SECRET_KEY
from utils.token import generar_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    datos = request.get_json()
    correo = datos.get('correo')
    password = datos.get('password')
    usuario = login_usuario(correo, password)
    if usuario:
        token = jwt.encode({
            'id': usuario['id'],
            'rol': usuario['rol'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        registrar_bitacora(
            id_usuario=usuario['id'],
            accion="Inicio de sesión exitoso",
            ip=request.remote_addr
        )

        return jsonify({"success": True, "token": token})
    else:
        return jsonify({"success": False, "mensaje": "Credenciales incorrectas"}), 401

# ✅ TOKEN PARA VISITANTE QUE SE REGISTRA AUTOMÁTICAMENTE
@auth_bp.route("/token/visitante", methods=["GET"])
def token_visitante():
    try:
        # 1. Crear usuario temporal en la BD (rol = cliente)
        id_usuario = registrar_visitante()

        # 2. Generar token con el ID real
        token = generar_token(id_usuario=id_usuario, rol="cliente")

        return jsonify({
            "success": True,
            "token": token,
            "rol": "cliente"
        })
    except Exception as e:
        print("❌ Error al generar token de visitante:", e)
        return jsonify({"success": False, "mensaje": "Error interno"}), 500
