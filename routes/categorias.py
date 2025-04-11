from flask import Blueprint, jsonify
from models.categoria import obtener_categorias
from utils.token import token_requerido

categorias_bp = Blueprint('categorias', __name__)

@categorias_bp.route('/categorias', methods=['GET'])
@token_requerido
def listar_categorias():
    categorias = obtener_categorias()
    return jsonify({"categorias": categorias})
