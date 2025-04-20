# 📁 routes/stripe_pago.py

from flask import Blueprint, request, jsonify
import os
import stripe
from flask import Blueprint, request, jsonify

# Reemplaza esto con tu clave secreta real de Stripe
import os
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

stripe_pago_bp = Blueprint("stripe_pago", __name__)

@stripe_pago_bp.route("/crear-pago", methods=["POST"])
def crear_pago():
    data = request.get_json()
    monto = int(data["monto"])  # en centavos (ej: 25.00 USD => 2500)
    descripcion = data.get("descripcion", "Compra Smart Cart")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                'price_data': {
                    'currency': 'usd',  # Cambia a 'bob' si usarás bolivianos y está habilitado en tu cuenta
                    'unit_amount': monto,
                    'product_data': {
                        'name': descripcion
                    },
                },
                'quantity': 1,
            }],
            
            mode='payment',
       
       #   success_url='http://192.168.0.12:5173/recibo/stripe-exitoso?id_carrito=' + str(data.get("id_carrito")),

success_url='https://checkout.stripe.com/success',  # no importa si existe o no
cancel_url = 'https://example.com/cancel'

        )
        return jsonify({'url': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 400



@stripe_pago_bp.route("/stripe-exito")
def stripe_exito():
    from flask import redirect

    id_carrito = request.args.get('id_carrito')
    if not id_carrito:
        return "Falta el ID del carrito", 400

    # Lógica para registrar la compra (esto puedes moverlo a un archivo aparte si quieres)
    from models.carrito import obtener_carrito_activo
    from models.compra import registrar_compra
    from models.detalle_carrito import calcular_total_productos, descontar_stock_carrito

    total = calcular_total_productos(id_carrito)
    id_compra = registrar_compra(id_carrito, total)

    if id_compra:
        descontar_stock_carrito(id_carrito)
        return redirect(f"smartcart://stripe-exitoso?id_compra={id_compra}")
    else:
        return "Error al registrar la compra", 500
