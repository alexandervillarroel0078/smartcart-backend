# routes/token.py
from flask import Blueprint, jsonify
from utils.token import generar_token
from config import conectar_db
import random
token_bp = Blueprint('token', __name__)

@token_bp.route('/token/visitante', methods=['GET'])
def token_visitante():
    conexion = conectar_db()
    cursor = conexion.cursor()
    correo = f"visitante{random.randint(1000, 9999)}@visitante.com"

    # Usamos id_rol = 4 (cliente)
    cursor.execute("""
    INSERT INTO usuarios (nombre, correo, id_rol)
    VALUES (%s, %s, %s) RETURNING id
""", ("Visitante", correo, 4))

    nuevo_id = cursor.fetchone()[0]
    conexion.commit()
    conexion.close()

    # Generamos el token con rol 'cliente' para control de permisos
    token = generar_token(nuevo_id, "cliente")
    return jsonify({"token": token})
