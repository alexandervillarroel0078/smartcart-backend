#  Dirección: utils/token.py
import jwt
from flask import request, jsonify, g
from functools import wraps
from flask import current_app as app
import datetime
 
def token_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'mensaje': 'Token mal formado'}), 400

        if not token:
            return jsonify({'mensaje': 'Token requerido'}), 401

        try:
            datos = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            g.usuario = datos  # ✅ AHORA FUNCIONA
        except jwt.ExpiredSignatureError:
            return jsonify({'mensaje': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'mensaje': 'Token inválido'}), 401

        return f(*args, **kwargs)
    return decorador

def token_requerido_rol(rol_requerido=None):
    def decorador_interno(f):
        @wraps(f)
        def decorador(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                try:
                    token = request.headers['Authorization'].split(" ")[1]
                except IndexError:
                    return jsonify({'mensaje': 'Token mal formado'}), 400

            if not token:
                return jsonify({'mensaje': 'Token requerido'}), 401

            try:
                datos = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                g.usuario = datos
                if rol_requerido and datos.get('rol') != rol_requerido:
                    return jsonify({"mensaje": "Acceso denegado"}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({'mensaje': 'Token expirado'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'mensaje': 'Token inválido'}), 401

            return f(*args, **kwargs)
        return decorador
    return decorador_interno

def generar_token(id_usuario, rol):
    payload = {
        "id": id_usuario,
        "rol": rol,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
    return token

