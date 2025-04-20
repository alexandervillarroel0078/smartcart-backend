# routes/inventario.py
from flask import Blueprint, send_file, jsonify, request
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from models.inventario import registrar_movimiento_inventario, obtener_alertas_bajo_stock
from utils.token import token_requerido
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from models.inventario import generar_reporte_inventario
from flask import g
import unicodedata
 
import unicodedata

def normalizar(texto):
    if not texto:
        return ""
    texto = texto.strip().lower()
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')

inventario_bp = Blueprint('inventario', __name__)



def normalizar(texto):
    if not texto:
        return ""
    texto = texto.strip().lower()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# Ruta para registrar entrada o salida de inventario
@inventario_bp.route('/inventario/movimiento', methods=['POST'])
@token_requerido
def registrar_movimiento():
    if request.usuario['rol'] not in ['almacenero', 'admin']:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    datos = request.get_json()
    id_producto = datos.get('id_producto')
    tipo = datos.get('tipo')  # 'entrada' o 'salida'
    cantidad = datos.get('cantidad')
    motivo = datos.get('motivo')

    exito = registrar_movimiento_inventario(id_producto, tipo, cantidad, motivo)
    if exito:
        return jsonify({"success": True, "mensaje": "Movimiento registrado correctamente"})
    else:
        return jsonify({"success": False, "mensaje": "Error al registrar movimiento"}), 500

# Ruta para obtener productos 
@inventario_bp.route('/inventario/alertas', methods=['GET'])
@token_requerido
def alertas_bajo_stock():
    if g.usuario['rol'] not in ['almacenero', 'admin']:  # ✅ aquí va `g.usuario`
        return jsonify({"mensaje": "Acceso denegado"}), 403

    alertas = obtener_alertas_bajo_stock()
    return jsonify({"alertas": alertas})



@inventario_bp.route("/inventario/reporte", methods=["GET"])
@token_requerido
def obtener_reporte_inventario():
    datos = generar_reporte_inventario()

    estado_filtro = request.args.get("estado")
    categoria_filtro = request.args.get("categoria")

    if estado_filtro:
        filtro_normalizado = normalizar(estado_filtro)
        datos = [p for p in datos if normalizar(p["estado"]) == filtro_normalizado]

    if categoria_filtro:
        categoria_normalizada = normalizar(categoria_filtro)
        datos = [p for p in datos if normalizar(p["categoria"]) == categoria_normalizada]

    return jsonify(datos)






@inventario_bp.route("/inventario/reporte/pdf")
def descargar_reporte_pdf():
    from utils.helpers import normalizar  # asegúrate de que este import funciona
    estado_filtro = request.args.get("estado")
    categoria_filtro = request.args.get("categoria")

    data = generar_reporte_inventario()
    print("📄 Generando PDF con productos:", len(data))

    if estado_filtro:
        filtro_estado = normalizar(estado_filtro)
        data = [p for p in data if normalizar(p["estado"]) == filtro_estado]

    if categoria_filtro:
        filtro_categoria = normalizar(categoria_filtro)
        data = [p for p in data if normalizar(p["categoria"]) == filtro_categoria]

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, height - 40, "Reporte de Inventario")

    c.setFont("Helvetica", 10)
    y = height - 70
    headers = ["ID", "Nombre", "Modelo", "Stock", "Mínimo", "Máximo", "Estado"]
    for i, h in enumerate(headers):
        c.drawString(40 + i * 70, y, h)

    y -= 20
    for item in data:
        fila = [
            str(item["id"]),
            item["nombre"],
            item.get("modelo") if item.get("modelo") else "-",
            str(item["stock"]),
            str(item["umbral_minimo"]),
            str(item["umbral_maximo"]),
            item["estado"]
        ]
        for i, val in enumerate(fila):
            texto = str(val) if val is not None else "-"
            c.drawString(40 + i * 70, y, texto[:15])
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="reporte_inventario.pdf",
        mimetype="application/pdf"
    )

@inventario_bp.route("/inventario/reporte/excel")
@token_requerido
def descargar_reporte_excel():
    estado_filtro = request.args.get("estado")
    categoria_filtro = request.args.get("categoria")

    data = generar_reporte_inventario()

    if estado_filtro:
        estado_normalizado = normalizar(estado_filtro)
        data = [p for p in data if normalizar(p["estado"]) == estado_normalizado]

    if categoria_filtro:
        categoria_normalizada = normalizar(categoria_filtro)
        data = [p for p in data if normalizar(p["categoria"]) == categoria_normalizada]

    df = pd.DataFrame(data)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Inventario")
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="reporte_inventario.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@inventario_bp.route("/inventario/reporte/csv")
@token_requerido
def descargar_reporte_csv():
    estado_filtro = request.args.get("estado")
    categoria_filtro = request.args.get("categoria")

    data = generar_reporte_inventario()

    if estado_filtro:
        estado_normalizado = normalizar(estado_filtro)
        data = [p for p in data if normalizar(p["estado"]) == estado_normalizado]

    if categoria_filtro:
        categoria_normalizada = normalizar(categoria_filtro)
        data = [p for p in data if normalizar(p["categoria"]) == categoria_normalizada]

    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="reporte_inventario.csv",
        mimetype="text/csv"
    )
