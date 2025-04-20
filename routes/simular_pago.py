# 📁 routes/simular_pago.py

from flask import Blueprint, request, jsonify, g
from models.pago import registrar_pago
from models.compra import registrar_compra
from models.carrito import obtener_carrito_activo
from models.detalle_carrito import calcular_total_productos
from models.bitacora import registrar_bitacora
from utils.token import token_requerido
from models.carrito import cerrar_carrito
simular_pago_bp = Blueprint("simular_pago", __name__)

@simular_pago_bp.route('/simular-pago-v2', methods=['POST'])
@token_requerido
def simular_pago():
    print("🧪 Request JSON completo:", request.get_json())

    id_usuario = g.usuario['id']
    metodo_pago = request.json.get('metodo_pago', 'Simulado')
    estado = request.json.get('estado', 'exitoso')

    # ✅ NUEVO: permitir enviar el id_carrito manualmente (opcional)
    id_carrito = request.json.get('id_carrito')
    if not id_carrito:
        id_carrito = obtener_carrito_activo(id_usuario)

    if not id_carrito:
        return jsonify({"success": False, "mensaje": "No tienes un carrito activo"}), 400

    # Calcular total
    total = calcular_total_productos(id_carrito)

    # 🆕 Leer datos opcionales
    nombre_cliente = request.json.get('nombre_cliente')
    nit_cliente = request.json.get('nit_cliente')
    print("📦 nombre_cliente:", nombre_cliente)
    print("📦 nit_cliente:", nit_cliente)

    # Registrar compra con nombre y nit
    id_compra = registrar_compra(
    id_carrito=id_carrito,
    total=total,
    nombre_cliente=nombre_cliente,
    nit_cliente=nit_cliente,
    metodo_pago=metodo_pago
    )
    if not id_compra:
        return jsonify({"success": False, "mensaje": "Error al registrar compra"}), 500

    # Registrar pago simulado
    exito = registrar_pago(id_compra, total, metodo_pago, estado)
    if not exito:
        return jsonify({"success": False, "mensaje": "Error al registrar pago"}), 500
    cerrar_carrito(id_carrito)
    # Registrar en bitácora
    registrar_bitacora(id_usuario, f"Simuló pago de compra ID {id_compra}", request.remote_addr)

    return jsonify({
        "success": True,
        "mensaje": "Pago simulado exitosamente",
        "total": total,
        "metodo_pago": metodo_pago,
        "estado": estado,
        "id_compra": id_compra,  # ✅ Agregado aquí
         "id_carrito": id_carrito, 
    }), 200
