# 📁 routes/token.py
from flask import Blueprint, jsonify
from utils.token import generar_token
from config import conectar_db
import random
from models.carrito import cerrar_carritos_abiertos, crear_carrito

token_bp = Blueprint('token', __name__)

@token_bp.route('/token/visitante', methods=['GET'])
def token_visitante():
    conexion = conectar_db()
    cursor = conexion.cursor()
    correo = f"visitante{random.randint(1000, 9999)}@visitante.com"

    # Crear usuario visitante
    cursor.execute("""
        INSERT INTO usuarios (nombre, correo, id_rol)
        VALUES (%s, %s, %s) RETURNING id
    """, ("Visitante", correo, 4))  # rol cliente
    nuevo_id = cursor.fetchone()[0]
    conexion.commit()
    conexion.close()

    # ✅ Cerrar carritos anteriores por si acaso
    cerrar_carritos_abiertos(nuevo_id)

    # ✅ Crear un nuevo carrito
    crear_carrito(nuevo_id)

    # ✅ Generar token
    token = generar_token(nuevo_id, "cliente")
    return jsonify({
    "token": token,
    "id": nuevo_id  # 👈 este valor es el que espera Flutter
})
