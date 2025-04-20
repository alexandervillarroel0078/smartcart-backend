# 📁 routes/stripe.py

from flask import Blueprint, request, jsonify, g
import stripe
 
from models.carrito import obtener_carrito_activo
from models.compra import registrar_compra
from models.pago import registrar_pago
from models.carrito import cerrar_carrito
from models.detalle_carrito import calcular_total_productos
from models.bitacora import registrar_bitacora

 
stripe_bp = Blueprint('stripe', __name__)

@stripe_bp.route('/crear-pago', methods=['POST'])
def crear_pago_stripe():
    data = request.get_json()
    monto = data['monto']
    descripcion = data['descripcion']
    id_carrito = data['id_carrito']

    # Calcular total real y registrar compra (simulado)
    total = calcular_total_productos(id_carrito)
    nombre_cliente = data.get("nombre_cliente")
    nit_cliente = data.get("nit_cliente")

    id_compra = registrar_compra(
        id_carrito=id_carrito,
        total=total,
        nombre_cliente=nombre_cliente,
        nit_cliente=nit_cliente,
        metodo_pago="Stripe"
    )

    if not id_compra:
        return jsonify({"success": False, "mensaje": "Error al registrar compra"}), 500

    print("✅ ID compra generado:", id_compra)

    # ✅ SUCCESS y CANCEL URLS
    success_url = f'smartcart://stripe-exitoso?id_compra={id_compra}'
    cancel_url = 'https://tupagina.com/cancelado'  # temporal

    print("✅ Redireccionando a:", success_url)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'BOB',
                    'product_data': {'name': descripcion},
                    'unit_amount': monto,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return jsonify({'url': session.url}), 200

    except Exception as e:
        print("❌ Error al crear sesión Stripe:", str(e))
        return jsonify({'error': str(e)}), 500
