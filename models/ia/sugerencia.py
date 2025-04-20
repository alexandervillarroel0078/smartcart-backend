from config import conectar_db
from models.ia.apriori import obtener_compras_agrupadas, generar_reglas_asociacion, sugerencias_por_apriori
from models.carrito import obtener_carrito_activo
from models.detalle_carrito import listar_productos_carrito_para_ia

from models.producto import obtener_producto_por_id
def obtener_sugerencias_basicas(id_usuario):
    conn = conectar_db()

    # Obtener historial de transacciones
    transacciones = obtener_compras_agrupadas(conn)
    print("📦 Transacciones agrupadas:", transacciones)

    reglas = generar_reglas_asociacion(transacciones)
    print("📊 Reglas generadas:", dict(reglas))  # cast para ver el defaultdict

    # Obtener productos actuales en el carrito
    id_carrito = obtener_carrito_activo(id_usuario)
    print("🛒 ID carrito activo:", id_carrito)

    productos_en_carrito = [p['id_producto'] for p in listar_productos_carrito_para_ia(id_carrito)]
    print("🛒 Productos en carrito:", productos_en_carrito)

    # Generar sugerencias por Apriori
    ids_sugeridos = sugerencias_por_apriori(productos_en_carrito, reglas)
    print("💡 IDs sugeridos:", ids_sugeridos)

    # Obtener datos completos de los productos sugeridos
    sugerencias = []
    for pid in ids_sugeridos:
        prod = obtener_producto_por_id(pid)
        if prod:
            sugerencias.append(prod)

    print("✅ Sugerencias finales:", sugerencias)
    return sugerencias
