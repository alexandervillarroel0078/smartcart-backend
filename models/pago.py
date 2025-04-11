from config import conectar_db
from datetime import datetime

#def registrar_pago(id_carrito, monto, metodo_pago):
def registrar_pago(id_compra, monto, metodo_pago):
    conexion = conectar_db()
    if conexion is None:
        return False

    try:
        cursor = conexion.cursor()
        # Crear un nuevo registro de pago
        cursor.execute("""
            INSERT INTO pagos (id_compra, monto, metodo_pago, estado)
            VALUES (%s, %s, %s, 'completado')
        """, (id_compra, monto, metodo_pago))

        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("❌ Error al registrar pago:", e)
        return False
