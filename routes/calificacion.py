from flask import Blueprint, request, jsonify, g
from config import conectar_db
from utils.token import token_requerido
from models.calificacion import guardar_calificacion

calificacion_bp = Blueprint('calificacion_bp', __name__)

@calificacion_bp.route('/calificaciones', methods=['POST'])
@token_requerido
def registrar_calificacion():
    data = request.get_json()
   
    id_compra = data.get("id_compra")
    estrellas = data.get("puntuacion")


    if not id_compra or not estrellas:
        return jsonify({"error": "Faltan datos"}), 400

    guardar_calificacion(id_compra, estrellas)
    return jsonify({"mensaje": "✅ Calificación guardada"}), 200
