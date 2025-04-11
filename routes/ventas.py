# routes/ventas.py
from flask import Blueprint, request, jsonify
from models.pago import registrar_pago
from models.detalle_carrito import validar_stock_carrito, descontar_stock_carrito, calcular_total_productos
from models.carrito import cerrar_carrito
from models.bitacora import registrar_bitacora
from utils.token import token_requerido
from models.compra import registrar_compra

from utils.descuentos import calcular_descuento_automatico
from config import conectar_db

ventas_bp = Blueprint('ventas', __name__)

@ventas_bp.route('/ventas/confirmar/<int:id_carrito>', methods=['POST'])
@token_requerido
def confirmar_venta(id_carrito):
      # ✅ Validar que solo cliente o cajero puedan confirmar venta
    if request.usuario['rol'] not in ['cajero', 'cliente']:
        return jsonify({"mensaje": "Acceso denegado"}), 403
    
    # 1. Validar stock
    validacion = validar_stock_carrito(id_carrito)
    if not validacion['exito']:
        return jsonify({"success": False, "mensaje": validacion['mensaje']}), 400

    # 2. Calcular total bruto
    total_bruto = calcular_total_productos(id_carrito)

    # 3. Calcular descuento automático
    descuento = calcular_descuento_automatico(total_bruto)

    # 4. Descontar stock
    if not descontar_stock_carrito(id_carrito):
        return jsonify({"success": False, "mensaje": "Error al descontar stock"}), 500

    # 5. Guardar el descuento en BD
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE carrito SET descuento = %s WHERE id = %s
            """, (descuento, id_carrito))
            conexion.commit()
            conexion.close()
        except Exception as e:
            print("❌ Error al guardar descuento:", e)

    # 6. Cerrar carrito
    if cerrar_carrito(id_carrito):
        registrar_bitacora(request.usuario['id'], f"Confirmó venta del carrito ID {id_carrito}", request.remote_addr)
        return jsonify({
            "success": True,
            "mensaje": "Venta confirmada y carrito cerrado",
            "total_bruto": total_bruto,
            "descuento": descuento,
            "total_final": total_bruto - descuento
        }), 200
    else:
        return jsonify({"success": False, "mensaje": "Error al cerrar carrito"}), 500
    

@ventas_bp.route('/ventas/pagar/<int:id_carrito>', methods=['POST'])
@token_requerido
def gestionar_pago(id_carrito):
    id_usuario = request.usuario['id']
    total = calcular_total_productos(id_carrito)
    metodo_pago = request.json.get('metodo_pago', 'Tarjeta de Crédito')
    # 1. Registrar compra
    id_compra = registrar_compra(id_carrito, total)
    if not id_compra:
        return jsonify({"success": False, "mensaje": "Error al registrar compra"}), 500

    # 2. Registrar pago (con total agregado ✅)
    exito = registrar_pago(id_compra=id_compra, monto=total, metodo_pago=metodo_pago)
    if exito:
        registrar_bitacora(id_usuario, f"Registró pago para la compra ID {id_compra}", request.remote_addr)
        return jsonify({
            "success": True,
            "mensaje": "Pago registrado correctamente",
            "total": total,
            "metodo_pago": metodo_pago
        }), 200
    else:
        return jsonify({"success": False, "mensaje": "Error al registrar pago"}), 500

