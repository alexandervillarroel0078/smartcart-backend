# models/ia/apriori.py

from collections import defaultdict

# Simula una consulta: [{id_compra: 1, id_producto: 5}, {id_compra: 1, id_producto: 6}, ...]
def obtener_compras_agrupadas(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_carrito, id_producto
FROM detalle_carrito
WHERE id_carrito IS NOT NULL

    """)
    resultados = cursor.fetchall()

    # Agrupar productos por compra
    compras = defaultdict(set)
    for id_compra, id_producto in resultados:
        compras[id_compra].add(id_producto)

    return list(compras.values())  # [[5, 6], [6, 7], [5, 8], ...]

# Genera reglas simples como: si compras A, también compras B
def generar_reglas_asociacion(transacciones):
    reglas = defaultdict(lambda: defaultdict(int))

    for trans in transacciones:
        for producto_a in trans:
            for producto_b in trans:
                if producto_a != producto_b:
                    reglas[producto_a][producto_b] += 1

    return reglas

# Dado un carrito, sugiere productos según reglas
def sugerencias_por_apriori(productos_en_carrito, reglas, limite=3):
    sugerencias = defaultdict(int)

    for prod in productos_en_carrito:
        for sugerido, score in reglas.get(prod, {}).items():
            if sugerido not in productos_en_carrito:
                sugerencias[sugerido] += score

    # Ordenar por score
    sugeridos_ordenados = sorted(sugerencias.items(), key=lambda x: x[1], reverse=True)
    return [prod_id for prod_id, _ in sugeridos_ordenados[:limite]]
