# models/compra.py
from config import conectar_db
from datetime import datetime

# Registrar una compra sin id_cliente (usa solo carrito y total)
def registrar_compra(id_carrito, total, nombre_cliente=None, nit_cliente=None, metodo_pago="Simulado"):
    print("🚨 ENTRANDO A FUNCION registrar_compra CORRECTA 🚨")
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            
            print("🧾 VALORES A INSERTAR:")
            print("carrito:", id_carrito)
            print("total:", total)
            print("nombre_cliente:", nombre_cliente)
            print("nit_cliente:", nit_cliente)
            print("metodo_pago:", metodo_pago)

            cursor.execute("""
                INSERT INTO compras (id_carrito, total, nombre_cliente, nit_cliente, metodo_pago, fecha)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                id_carrito,
                total,
                nombre_cliente,
                nit_cliente,
                metodo_pago,
                datetime.now()
            ))

            id_nueva_compra = cursor.fetchone()[0]
            conexion.commit()
            conexion.close()
            return id_nueva_compra
        except Exception as e:
            print("❌ Error al registrar compra:", e)
            return None



# 📁 models/compra.py
def obtener_detalle_compra(id_compra):
    from config import conectar_db
    import time

    conexion = conectar_db()
    if not conexion:
        return None

    try:
        cursor = conexion.cursor()

        # ✅ 1. Datos generales de la compra
        cursor.execute("""
            SELECT c.id, c.total, ca.descuento, (c.total - ca.descuento) AS total_final, c.fecha,
       c.nombre_cliente, c.nit_cliente
FROM compras c
JOIN carrito ca ON ca.id = c.id_carrito
WHERE c.id = %s

        """, (id_compra,))
        compra = cursor.fetchone()

        if not compra:
            print("❌ Compra no encontrada")
            return None

        compra_dict = {
            "id": compra[0],
            "total": float(compra[1]),
            "descuento": float(compra[2] or 0),
            "total_final": float(compra[3]),
            "fecha": compra[4].strftime("%Y-%m-%d %H:%M"),
            "nombre_cliente": compra[5],
            "nit_cliente": compra[6],
            "productos": []
        }

        # ✅ 2. Reintentar hasta 3 veces si no hay productos todavía
        intento = 1
        productos = []
        while intento <= 3 and not productos:
            cursor.execute("""
                SELECT p.nombre, dc.cantidad, dc.precio_unitario * dc.cantidad AS subtotal
                FROM detalle_carrito dc
                JOIN productos p ON p.id = dc.id_producto
                WHERE dc.id_carrito = (
                    SELECT id_carrito FROM compras WHERE id = %s
                )
            """, (id_compra,))
            productos = cursor.fetchall()
            if productos:
                break

            if not productos:
                print(f"⚠️ Intento {intento}: Aún no hay productos en el carrito.")
                time.sleep(0.8)  # espera 300ms
                intento += 1

        if not productos:
            print("❌ No se encontraron productos aún en el carrito (incompleto).")
            return None  # Esto provocará un 404

        print("📦 Productos obtenidos del carrito:")
        for producto in productos:
            print("🔹", producto)
            compra_dict["productos"].append({
                "producto": producto[0],
                "cantidad": producto[1],
                "subtotal": float(producto[2])
            })
        print("✅ Productos encontrados:", compra_dict["productos"])
        conexion.close()
        return compra_dict

    except Exception as e:
        print("❌ Error al obtener detalle de compra:", e)
        return None
