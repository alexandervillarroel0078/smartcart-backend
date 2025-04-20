from datetime import datetime

def calcular_descuento_automatico(total):
    """
    Aplica un 10% de descuento si:
    - El total es mayor o igual a Bs 300
    - Y la fecha está entre el 1 y 30 de abril de 2025
    """
    hoy = datetime.now().date()
    fecha_inicio = datetime(2025, 4, 1).date()
    fecha_fin = datetime(2025, 4, 30).date()

    if total >= 5000:
        return total * 0.1  # 10% de descuento
    return 0
