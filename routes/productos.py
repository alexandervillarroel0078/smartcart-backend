# Paso 1: Crear carpetas y archivos
# Estructura esperada:
# - routes/productos.py
# - routes/usuarios.py
# - routes/auth.py
# - models/
# - app.py (afuera)

# Archivo: routes/productos.py
from flask import Blueprint,request, jsonify, g
from models.producto import (obtener_productos, 
 registrar_producto, editar_producto, eliminar_producto,sumar_stock_producto,
 obtener_productos_paginados,obtener_productos_catalogo)
from models.bitacora import registrar_bitacora
from utils.token import token_requerido
from config import conectar_db
from flask_cors import cross_origin

productos_bp = Blueprint('productos', __name__)

# AGREGAR PRODUCTO
@productos_bp.route('/productos/agregar', methods=['POST'])
@token_requerido
def agregar_producto():
    if g.usuario['rol'] != 'almacenero':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    datos = request.get_json()
    nombre = datos.get('nombre')
    descripcion = datos.get('descripcion')
    precio = datos.get('precio')
    stock = datos.get('stock')
    umbral_stock = datos.get('umbral_stock')  # ✅ asegurarse de obtenerlo del JSON
    id_categoria = datos.get('id_categoria')
    visible = datos.get('visible', True)  # True por defecto
    exito = registrar_producto(nombre, descripcion, precio, stock, umbral_minimo, umbral_maximo, modelo, id_categoria, imagen, visible)
    if exito:
        registrar_bitacora(
            id_usuario=g.usuario['id'],
            accion=f"Agregó producto: {nombre}",
            ip=request.remote_addr
        )
        return jsonify({"success": True, "mensaje": "Producto registrado correctamente"})
    else:
        return jsonify({"success": False, "mensaje": "Error al registrar producto"}), 500

# EDITAR PRODUCTO
@productos_bp.route('/productos/editar/<int:id>', methods=['PUT'])
@token_requerido
def editar_producto_ruta(id):
    if g.usuario['rol'] != 'almacenero':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    datos = request.get_json()
    exito = editar_producto(
        id,
        datos.get('nombre'),
        datos.get('descripcion'),
        datos.get('precio'),
        datos.get('stock'),
        datos.get('umbral_maximo'), 
        datos.get('id_categoria')
    )
    if exito:
        registrar_bitacora(
            id_usuario=g.usuario['id'],
            accion=f"Editó producto ID: {id}",
            ip=request.remote_addr
        )
        return jsonify({"success": True, "mensaje": "Producto actualizado"})
    else:
        return jsonify({"success": False, "mensaje": "Error al actualizar"}), 500

# ELIMINAR PRODUCTO
@productos_bp.route('/productos/eliminar/<int:id>', methods=['DELETE'])
@token_requerido
def eliminar_producto_ruta(id):
    if g.usuario['rol'] != 'almacenero':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    exito = eliminar_producto(id)
    if exito:
        registrar_bitacora(
            id_usuario=g.usuario['id'],
            accion=f"Eliminó producto ID: {id}",
            ip=request.remote_addr
        )
        return jsonify({"success": True, "mensaje": "Producto eliminado"})
    else:
        return jsonify({"success": False, "mensaje": "Error al eliminar"}), 500


@productos_bp.route('/productos/<int:id>', methods=['GET'])
@token_requerido
def obtener_producto(id):
    conexion = conectar_db()
    if conexion is None:
        return jsonify({"mensaje": "Error de conexión"}), 500

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock, 
                   p.umbral_minimo, p.umbral_maximo, p.modelo, p.id_categoria
            FROM productos p
            WHERE p.id = %s
        """, (id,))
        producto = cursor.fetchone()
        conexion.close()

        if producto:
            return jsonify({
                "id": producto[0],
                "nombre": producto[1],
                "descripcion": producto[2],
                "precio": float(producto[3]),
                "stock": producto[4],
                "umbral_minimo": producto[5],
                "umbral_maximo": producto[6],
                "modelo": producto[7],
                "id_categoria": producto[8]
            })
        else:
            return jsonify({"mensaje": "Producto no encontrado"}), 404
    except Exception as e:
        print("❌ Error al obtener producto:", e)
        return jsonify({"mensaje": "Error interno"}), 500

# routes/productos.py
@productos_bp.route('/productos/alertas')
@token_requerido
def alertas_stock():
    if g.usuario['rol'] != 'almacenero':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    conexion = conectar_db()
    if not conexion:
        return jsonify({"mensaje": "Error de conexión"}), 500

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT p.id, p.nombre, p.stock, p.umbral_stock, c.nombre AS categoria
            FROM productos p
            JOIN categorias c ON p.id_categoria = c.id
            WHERE p.stock <= p.umbral_stock
        """)
        productos = cursor.fetchall()
        conexion.close()

        alertas = [{
            "id": p[0],
            "nombre": p[1],
            "stock": p[2],
            "umbral_stock": p[3],
            "categoria": p[4],
        } for p in productos]

        return jsonify({"alertas": alertas})
    except Exception as e:
        print("❌ Error al obtener alertas de stock:", e)
        return jsonify({"mensaje": "Error interno"}), 500

@productos_bp.route('/productos/<int:id>/entrada', methods=['PUT'])
@token_requerido
def registrar_entrada_producto(id):
    if g.usuario['rol'] != 'almacenero':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    datos = request.get_json()
    cantidad = datos.get('cantidad')

    if cantidad is None or cantidad <= 0:
        return jsonify({"mensaje": "Cantidad inválida"}), 400

    from models.producto import sumar_stock_producto
    exito = sumar_stock_producto(id, cantidad)

    if exito:
        from models.bitacora import registrar_bitacora
        registrar_bitacora(
            id_usuario=g.usuario['id'],
            accion=f"Sumó {cantidad} unidades al producto ID {id}",
            ip=request.remote_addr
        )
        return jsonify({"success": True, "mensaje": "Stock actualizado"})
    else:
        return jsonify({"success": False, "mensaje": "Error al actualizar stock"}), 500

@productos_bp.route('/productos/stock/<int:id>', methods=['PUT'])
@token_requerido
def actualizar_stock(id):
    if g.usuario['rol'] != 'almacenero':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    datos = request.get_json()
    cantidad = datos.get("cantidad")

    if cantidad is None or int(cantidad) <= 0:
        return jsonify({"mensaje": "Cantidad inválida"}), 400

    exito = sumar_stock_producto(
        id_producto=id,
        cantidad=int(cantidad),
        id_usuario=g.usuario['id'],  # ✅ CORREGIDO AQUÍ
        observacion="Actualización manual de stock desde frontend"
    )

    if exito:
        registrar_bitacora(
            id_usuario=g.usuario['id'],
            accion=f"Aumentó stock del producto ID {id} en +{cantidad}",
            ip=request.remote_addr
        )
        return jsonify({"mensaje": "Stock actualizado", "success": True})
    else:
        return jsonify({"mensaje": "Error al actualizar stock", "success": False}), 500

@productos_bp.route('/productos/<int:id>/visibilidad', methods=['PUT'])
@token_requerido
@cross_origin()
def actualizar_visibilidad(id):
    if g.usuario['rol'] != 'almacenero':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    datos = request.get_json()
    visible = datos.get('visible')  # ⚠️ OJO: esto puede ser None si no se envía

    if visible is None:
        return jsonify({"mensaje": "Falta el campo 'visible'"}), 400

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("UPDATE productos SET visible = %s WHERE id = %s", (visible, id))
        conexion.commit()
        conexion.close()
        return jsonify({"mensaje": "Visibilidad actualizada", "success": True})
    except Exception as e:
        print("❌ Error al actualizar visibilidad:", e)
        return jsonify({"mensaje": "Error interno"}), 500

@productos_bp.route('/productos', methods=['GET'])
@token_requerido
@cross_origin()
def listar_productos():
    try:
        pagina = int(request.args.get("pagina", 1))  # ✅ se puede cambiar vía query param
        productos = obtener_productos_paginados(pagina)
        return jsonify({"productos": productos})
    except Exception as e:
        print("❌ Error en la ruta de productos:", e)
        return jsonify({"mensaje": "Error interno"}), 500
     
@productos_bp.route('/catalogo', methods=['GET'])
@token_requerido
def ver_catalogo():
    conexion = conectar_db()
    if conexion is None:
        return jsonify({"mensaje": "Error de conexión"}), 500

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock, p.imagen,
                   p.id_categoria, c.nombre AS categoria
            FROM productos p
            JOIN categorias c ON p.id_categoria = c.id
            WHERE p.visible = TRUE
            ORDER BY p.nombre
        """)
        productos = cursor.fetchall()
        conexion.close()

        return jsonify({
            "productos": [
                {
                    "id": p[0],
                    "nombre": p[1],
                    "descripcion": p[2],
                    "precio": float(p[3]),
                    "stock": p[4],
                    "imagen": p[5],
                    "id_categoria": p[6],
                    "categoria": p[7],
                    "visible": True
                } for p in productos
            ]
        })
    except Exception as e:
        print("❌ Error al obtener productos del catálogo:", e)
        return jsonify({"mensaje": "Error interno"}), 500


@productos_bp.route('/productos/todos', methods=['GET'])
@token_requerido
def obtener_todos_los_productos():
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock,
                   p.umbral_minimo, p.umbral_maximo, p.modelo,
                   c.nombre AS categoria, p.visible, p.imagen
            FROM productos p
            JOIN categorias c ON p.id_categoria = c.id
            ORDER BY p.nombre ASC
        """)
        columnas = [desc[0] for desc in cursor.description]
        productos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        conexion.close()
        return jsonify({"productos": productos})
    except Exception as e:
        print("❌ Error al obtener todos los productos:", e)
        return jsonify({"mensaje": "Error interno"}), 500


@productos_bp.route('/productos/criticos', methods=['GET'])
@token_requerido
def obtener_productos_criticos():
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock,
                   p.umbral_minimo, p.umbral_maximo, p.modelo,
                   c.nombre AS categoria, p.visible, p.imagen
            FROM productos p
            JOIN categorias c ON p.id_categoria = c.id
            WHERE p.stock <= p.umbral_minimo
        """)
        columnas = [desc[0] for desc in cursor.description]
        productos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        conexion.close()
        return jsonify(productos)
    except Exception as e:
        print("❌ Error al obtener productos críticos:", e)
        return jsonify({"mensaje": "Error interno"}), 500

# Flask backend
@productos_bp.route('/productos/criticos', methods=['GET'])
@token_requerido
def productos_criticos():
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT * FROM productos
            WHERE stock <= umbral_minimo
            ORDER BY nombre ASC
        """)
        columnas = [desc[0] for desc in cursor.description]
        productos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        conexion.close()
        return jsonify({"productos": productos})
    except Exception as e:
        print("❌ Error al obtener productos críticos:", e)
        return jsonify({"mensaje": "Error interno"}), 500


 