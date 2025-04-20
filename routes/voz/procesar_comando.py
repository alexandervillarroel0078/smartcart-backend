# 📁 smart_cart_backend/routes/voz/procesar_comando.py

from flask import Blueprint, request, jsonify
from models.producto import obtener_producto_por_nombre
from models.detalle_carrito import agregar_producto as agregar_producto_al_carrito
from models.detalle_carrito import eliminar_producto as eliminar_producto_de_carrito
from models.detalle_carrito import calcular_total_productos, validar_stock_carrito, descontar_stock_carrito
from models.carrito import obtener_carrito_activo as obtener_carrito_activo_por_usuario, cerrar_carrito
from models.pago import registrar_pago
from utils.descuentos import calcular_descuento_automatico
from models.bitacora import registrar_bitacora
from models.detalle_carrito import listar_productos_carrito  # ✅ importar si no lo hiciste aún
from word2number import w2n
from routes.voz.utilidades_voz import convertir_numeros_en_texto  # asegúrate de tenerla ahí o en el mismo archivo
from models.detalle_carrito import eliminar_producto_de_carrito


procesar_comando_bp = Blueprint('procesar_comando', __name__)

@procesar_comando_bp.route('/voz/procesar', methods=['POST'])
def procesar_comando():
    data = request.get_json()
    texto = data.get('texto', '').strip()
    id_usuario = data.get('id_usuario')

    if not texto or not id_usuario:
        return jsonify({'error': 'Faltan datos'}), 400

    # Reinterpretar el texto para saber la acción
    from routes.voz.comandos_voz import interpretar_texto
    interpretacion = interpretar_texto(texto)
    print("🧠 Interpretación completa:", interpretacion)
    accion = interpretacion.get("accion")
    
    # Ejecutar acción
    if accion == "agregar":
        nombre_producto = interpretacion.get("producto", "")
        nombre_normalizado = convertir_numeros_en_texto(nombre_producto)
        producto = obtener_producto_por_nombre(nombre_normalizado)
        
        print("🧠 Nombre original:", nombre_producto)
        print("🔁 Nombre normalizado:", nombre_normalizado)
        print("🎯 Producto encontrado:", producto)
        
        if not producto:
           return jsonify({"error": f"Producto \"{nombre_producto}\" no encontrado"}), 404

        carrito_id = obtener_carrito_activo_por_usuario(id_usuario)
        if not carrito_id:
           return jsonify({"error": "No tienes carrito activo"}), 404

        agregar_producto_al_carrito(carrito_id, producto["id"], 1, producto["precio"])
        return jsonify({"mensaje": f"{producto['nombre']} agregado al carrito"}), 200
    
    elif accion == "aumentar":
        nombre_producto = interpretacion.get("producto", "")
        nombre_normalizado = convertir_numeros_en_texto(nombre_producto)
        producto = obtener_producto_por_nombre(nombre_normalizado)

        print("🧠 Nombre original:", nombre_producto)
        print("🔁 Nombre normalizado:", nombre_normalizado)
        print("🎯 Producto encontrado:", producto)

        if not producto:
            return jsonify({"error": f"Producto '{nombre_producto}' no encontrado"}), 404

        carrito_id = obtener_carrito_activo_por_usuario(id_usuario)
        if not carrito_id:
            return jsonify({"error": "No tienes carrito activo"}), 404

        # Aumentar 1 unidad del producto en el carrito
        agregado = agregar_producto_al_carrito(carrito_id, producto["id"], 1, producto["precio"])
        if agregado:
            return jsonify({"mensaje": f"Cantidad de {producto['nombre']} aumentada en el carrito"}), 200
        else:
            return jsonify({"error": "No se pudo aumentar cantidad"}), 500

    elif accion == "disminuir":
       nombre_producto = interpretacion.get("producto", "")
       nombre_normalizado = convertir_numeros_en_texto(nombre_producto)
       producto = obtener_producto_por_nombre(nombre_normalizado)

       print("🧠 Nombre original:", nombre_producto)
       print("🔁 Nombre normalizado:", nombre_normalizado)
       print("🎯 Producto encontrado:", producto)

       if not producto:
          return jsonify({"error": f"Producto \"{nombre_producto}\" no encontrado"}), 404

       carrito_id = obtener_carrito_activo_por_usuario(id_usuario)
       if not carrito_id:
          return jsonify({"error": "No tienes carrito activo"}), 404

       # Obtener productos del carrito
       from models.detalle_carrito import producto_en_carrito, actualizar_cantidad
       existente = producto_en_carrito(carrito_id, producto["id"])

       if not existente:
         return jsonify({"error": "Producto no está en el carrito"}), 404

       id_detalle, cantidad_actual = existente
       nueva_cantidad = cantidad_actual - 1

       if nueva_cantidad <= 0:
         eliminar_producto_de_carrito(carrito_id, producto["id"])
         return jsonify({"mensaje": f"{producto['nombre']} eliminado del carrito"}), 200
       else:
        actualizar_cantidad(id_detalle, nueva_cantidad)
        return jsonify({"mensaje": f"{producto['nombre']} ahora tiene {nueva_cantidad} unidades"}), 200

    elif accion == "quitar":
        nombre_producto = interpretacion.get("producto", "")
        nombre_normalizado = convertir_numeros_en_texto(nombre_producto)
        producto = obtener_producto_por_nombre(nombre_normalizado)
 
        print("🧠 Nombre original:", nombre_producto)
        print("🔁 Nombre normalizado:", nombre_normalizado)
        print("🎯 Producto encontrado:", producto)

        if not producto:
          return jsonify({"error": f"Producto \"{nombre_producto}\" no encontrado"}), 404

        carrito_id = obtener_carrito_activo_por_usuario(id_usuario)
        if not carrito_id:
          return jsonify({"error": "No tienes carrito activo"}), 404

        eliminar_producto_de_carrito(carrito_id, producto["id"])
        return jsonify({"mensaje": f"{producto['nombre']} eliminado del carrito"}), 200

    elif accion == 'ver_carrito':
        carrito_id = obtener_carrito_activo_por_usuario(id_usuario)
        if not carrito_id:
           return jsonify({'error': 'No tienes un carrito activo'}), 404

        productos = listar_productos_carrito(carrito_id)

        return jsonify({
        'mensaje': 'Carrito activo obtenido',
        "accion": "ver_carrito",  # 👈 AGREGA ESTA LÍNEA
        'carrito': {
            'id': carrito_id,
            'productos': productos
        }
        }), 200

    elif accion == "calcular_total":
        carrito_id = obtener_carrito_activo_por_usuario(id_usuario)
        if not carrito_id:
            return jsonify({"error": "No tienes carrito activo"}), 404
        total = calcular_total_productos(carrito_id)
        return jsonify({"mensaje": "Total calculado", "total": total}), 200

    elif accion == "pagar":
        carrito_id = obtener_carrito_activo_por_usuario(id_usuario)
        if not carrito_id:
            return jsonify({"error": "No tienes carrito activo"}), 404

        errores = validar_stock_carrito(carrito_id)
        if errores:
            return jsonify({"mensaje": "Stock insuficiente", "detalles": errores}), 400

        total = calcular_total_productos(carrito_id)
        descuento = calcular_descuento_automatico(total)
        descontar_stock_carrito(carrito_id)

        from config import conectar_db
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("UPDATE carrito SET descuento = %s WHERE id = %s", (descuento, carrito_id))
        conexion.commit()
        conexion.close()

        registrar_pago(carrito_id, total - descuento, metodo_pago="voz")

        cerrar_carrito(carrito_id)
        registrar_bitacora(id_usuario, f"Pagó con voz el carrito {carrito_id}", request.remote_addr)

        return jsonify({
            "mensaje": "Compra realizada con éxito",
            "total": total,
            "descuento": descuento,
            "total_final": total - descuento
        }), 200

    return jsonify({"mensaje": "Acción no reconocida"}), 400


  