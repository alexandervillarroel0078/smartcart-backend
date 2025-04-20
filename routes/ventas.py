# routes/ventas.py
from flask import Blueprint, request, jsonify,g
from models.pago import registrar_pago
from models.detalle_carrito import validar_stock_carrito, descontar_stock_carrito, calcular_total_productos
from models.carrito import cerrar_carrito
from models.bitacora import registrar_bitacora
from utils.token import token_requerido
from models.compra import registrar_compra
from utils.descuentos import calcular_descuento_automatico

from utils.descuentos import calcular_descuento_automatico
from config import conectar_db

ventas_bp = Blueprint('ventas', __name__)

# ✅ SOLO UNA VEZ ESTE DECORADOR:
@ventas_bp.route('/ventas/confirmar/<int:id_carrito>', methods=['POST'])
@token_requerido
def confirmar_venta(id_carrito):
    print(f"🛒 CONFIRMANDO VENTA PARA CARRITO ID: {id_carrito}")
    print(f"🔐 Usuario ID: {g.usuario['id']} | Rol: {g.usuario['rol']}")

    if g.usuario['rol'] not in ['cajero', 'cliente']:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    # 1. Validar stock
    errores_stock = validar_stock_carrito(id_carrito)
    if errores_stock:
        return jsonify({"success": False, "mensaje": "Stock insuficiente", "errores": errores_stock}), 400

    # 2. Calcular total
    total_bruto = calcular_total_productos(id_carrito)
    print(f"🧮 Total bruto del carrito: {total_bruto}")
    # 3. Calcular descuento automático
    descuento = calcular_descuento_automatico(total_bruto)
    print(f"🎯 Descuento aplicado: {descuento}")

    # 4. Guardar el descuento en el carrito
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("UPDATE carrito SET descuento = %s WHERE id = %s", (descuento, id_carrito))
        conexion.commit()
        conexion.close()
        print("✅ Descuento guardado en carrito correctamente")  # 👈 debug
    except Exception as e:
        print("❌ Error al guardar descuento:", e)

    # 5. Descontar stock
    #if not descontar_stock_carrito(id_carrito):
     
     #   print("❌ Error al descontar stock del carrito")
      #  return jsonify({"success": False, "mensaje": "Error al descontar stock"}), 500

    # 6. Cerrar carrito
    if cerrar_carrito(id_carrito):
        registrar_bitacora(g.usuario['id'], f"Confirmó venta del carrito ID {id_carrito}", request.remote_addr)
        return jsonify({
            "success": True,
            "mensaje": "Venta confirmada y carrito cerrado",
            "total_bruto": total_bruto,
            "descuento": descuento,
            "total_final": total_bruto - descuento
        }), 200
    else:
        print("❌ Error al cerrar carrito")
        return jsonify({"success": False, "mensaje": "Error al cerrar carrito"}), 500
   

@ventas_bp.route('/ventas/pagar/<int:id_carrito>', methods=['POST'])
@token_requerido
def gestionar_pago(id_carrito):
    id_usuario = g.usuario['id']
    total = calcular_total_productos(id_carrito)
    metodo_pago = request.json.get('metodo_pago', 'Tarjeta de Crédito')
    estado = request.json.get('estado', 'exitoso')

    # ✅ Corregido: ahora sí pasamos el id del cliente
    nombre_cliente = request.json.get('nombre_cliente')
    nit_cliente = request.json.get('nit_cliente')
    id_compra = registrar_compra(id_carrito, total, nombre_cliente, nit_cliente)

    if not id_compra:
        return jsonify({"success": False, "mensaje": "Error al registrar compra"}), 500
    #   Descontar stock justo después de registrar la compra
    if not descontar_stock_carrito(id_carrito):
        return jsonify({"success": False, "mensaje": "Error al descontar stock"}), 500

    exito = registrar_pago(id_compra=id_compra, monto=total, metodo_pago=metodo_pago, estado=estado)
    if exito:
        registrar_bitacora(id_usuario, f"Registró pago para la compra ID {id_compra}", request.remote_addr)
        return jsonify({
            "success": True,
            "mensaje": "Pago registrado correctamente",
            "total": total,
            "metodo_pago": metodo_pago,
            "id_compra": id_compra
        }), 200
    else:
        return jsonify({"success": False, "mensaje": "Error al registrar pago"}), 500



# =======================
# Simular Pago (Local)
# =======================
# Este endpoint simula un pago sin usar pasarela real como Stripe.
# Guarda el registro del pago en la tabla 'pagos' con estado "exitoso" o "fallido".
# Se utilizará mientras se desarrolla la lógica de pago real.
# Este endpoint debe llamarse después de confirmar la venta.
# Frontend puede enviar el método de pago y estado deseado (por defecto: exitoso)

 