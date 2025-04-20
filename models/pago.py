from config import conectar_db
from datetime import datetime

#def registrar_pago(id_carrito, monto, metodo_pago):
def registrar_pago(id_compra, monto, metodo_pago, estado='exitoso'):
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO pagos (id_compra, monto, metodo_pago, estado, fecha)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_compra, monto, metodo_pago, estado, datetime.now()))
            conexion.commit()
            conexion.close()
            return True
        except Exception as e:
            print("❌ Error al registrar pago:", e)
    return False