# routes/reportes_compras.py
from flask import Blueprint, request, jsonify, g, send_file
from config import conectar_db
from utils.token import token_requerido
import io
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from models.reportes_compras import obtener_reporte_compras
from models.reportes_compras import obtener_ventas_por_fecha

reportes_compras_bp = Blueprint('reportes_compras', __name__)


@reportes_compras_bp.route('/reporte-compras', methods=['GET'])
@token_requerido
def reporte_compras():
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    # Filtros desde query params
    fecha_inicio = request.args.get('inicio')
    fecha_fin = request.args.get('fin')
    nombre = request.args.get('nombre')
    nit = request.args.get('nit')
    monto_min = request.args.get('minimo')
    monto_max = request.args.get('maximo')

    compras = obtener_reporte_compras(fecha_inicio, fecha_fin, nombre, nit, monto_min, monto_max)
    return jsonify(compras), 200


@reportes_compras_bp.route('/reporte-compras/excel', methods=['GET'])
@token_requerido
def exportar_compras_excel():
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    compras = obtener_reporte_compras()

    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte Compras"
    ws.append(["ID", "Carrito", "Total", "Fecha", "Cliente", "NIT"])
    for compra in compras:
        ws.append([
            compra['id'],
            compra['id_carrito'],
            compra['total'],
            compra['fecha'],
            compra['cliente'],
            compra['nit_cliente']
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="reporte_compras.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Exportar a PDF 2
@reportes_compras_bp.route('/reporte-compras/pdf', methods=['GET'])
@token_requerido
def exportar_compras_pdf():
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    compras = obtener_reporte_compras()

    output = io.BytesIO()
    pdf = canvas.Canvas(output, pagesize=(595, 842))

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(297, 800, "📋 Reporte de Compras")

    y = 770
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(40, y, "ID")
    pdf.drawString(70, y, "Carrito")
    pdf.drawString(130, y, "Total")
    pdf.drawString(190, y, "Fecha")
    pdf.drawString(310, y, "Cliente")
    pdf.drawString(450, y, "NIT")

    pdf.setFont("Helvetica", 10)
    y -= 20
    for compra in compras:
        pdf.drawString(40, y, str(compra['id']))
        pdf.drawString(70, y, str(compra['id_carrito']))
        pdf.drawString(130, y, f"Bs {compra['total']}")
        pdf.drawString(190, y, str(compra['fecha']))
        pdf.drawString(310, y, str(compra['cliente']))
        pdf.drawString(450, y, str(compra['nit_cliente']))
        y -= 18
        if y < 50:
            pdf.showPage()
            y = 800

    pdf.save()
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="reporte_compras.pdf",
        mimetype="application/pdf"
    )
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, id_carrito, total, fecha, 
                   COALESCE(nombre_cliente, 'No registrado'), 
                   COALESCE(nit_cliente, 'No registrado')
            FROM compras
            ORDER BY fecha DESC
        """)
        compras = cursor.fetchall()
        conexion.close()

        output = io.BytesIO()
        pdf = canvas.Canvas(output, pagesize=(595, 842))  # A4 size

        # Título
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawCentredString(297, 800, "📋 Reporte de Compras")

        # Cabecera
        y = 770
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(40, y, "ID")
        pdf.drawString(70, y, "Carrito")
        pdf.drawString(130, y, "Total")
        pdf.drawString(190, y, "Fecha")
        pdf.drawString(310, y, "Cliente")
        pdf.drawString(450, y, "NIT")

        # Datos
        pdf.setFont("Helvetica", 10)
        y -= 20
        for compra in compras:
            id, carrito, total, fecha, cliente, nit = compra
            pdf.drawString(40, y, str(id))
            pdf.drawString(70, y, str(carrito))
            pdf.drawString(130, y, f"Bs {total}")
            pdf.drawString(190, y, fecha.strftime("%Y-%m-%d %H:%M:%S"))
            pdf.drawString(310, y, str(cliente))
            pdf.drawString(450, y, str(nit))
            y -= 18
            if y < 50:
                pdf.showPage()
                y = 800

        pdf.save()
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="reporte_compras.pdf",
            mimetype="application/pdf"
        )

    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, id_carrito, total, fecha, 
                   COALESCE(nombre_cliente, 'No registrado'), 
                   COALESCE(nit_cliente, 'No registrado')
            FROM compras
            ORDER BY fecha DESC
        """)
        compras = cursor.fetchall()
        conexion.close()

        output = io.BytesIO()
        pdf = canvas.Canvas(output)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(200, 800, "Reporte de Compras")

        y = 760
        pdf.setFont("Helvetica", 10)
        for compra in compras:
            pdf.drawString(40, y, f"ID: {compra[0]}, Carrito: {compra[1]}, Total: Bs {compra[2]}, Fecha: {compra[3]}, Cliente: {compra[4]}, NIT: {compra[5]}")
            y -= 20
            if y < 40:
                pdf.showPage()
                y = 780

        pdf.save()
        output.seek(0)

        return send_file(output, as_attachment=True, download_name="reporte_compras.pdf", mimetype="application/pdf")
    

# 📁 smartcart-backend/routes/reportes_compras.py
from models.reportes_compras import obtener_productos_mas_vendidos

@reportes_compras_bp.route('/reporte-productos-mas-vendidos', methods=['GET'])
@token_requerido
def productos_mas_vendidos():
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    fecha_inicio = request.args.get('inicio')
    fecha_fin = request.args.get('fin')
    limite = int(request.args.get('limite', 5))  # por defecto top 5

    datos = obtener_productos_mas_vendidos(fecha_inicio, fecha_fin, limite)
    return jsonify(datos), 200


 
@reportes_compras_bp.route('/grafica-ventas-por-fecha', methods=['GET'])
@token_requerido
def grafica_ventas_por_fecha():
    if g.usuario['rol'] != 'admin':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    fecha_inicio = request.args.get('inicio')
    fecha_fin = request.args.get('fin')
    agrupacion = request.args.get('modo', 'dia')  # 'dia' o 'mes'

    datos = obtener_ventas_por_fecha(fecha_inicio, fecha_fin, agrupacion)
    return jsonify(datos), 200










