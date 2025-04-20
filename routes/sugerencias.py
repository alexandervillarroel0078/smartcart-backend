# routes/sugerencias.py
from flask import Blueprint, jsonify
from models.ia.sugerencia import obtener_sugerencias_basicas

sugerencias_bp = Blueprint("sugerencias", __name__)

@sugerencias_bp.route('/sugerencias/<int:id_usuario>', methods=['GET'])
def sugerencias_usuario(id_usuario):
    sugerencias = obtener_sugerencias_basicas(id_usuario)
    return jsonify({"sugerencias": sugerencias})
