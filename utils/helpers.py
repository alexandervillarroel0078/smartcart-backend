# utils/helpers.py

import re
import unicodedata

def normalizar(texto):
    """Convierte a minúsculas y elimina tildes/acentos para comparar mejor."""
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto

def formatear_moneda(valor):
    """Devuelve el valor con formato Bs XX.XX"""
    try:
        return f"Bs {float(valor):.2f}"
    except (ValueError, TypeError):
        return "Bs 0.00"

def es_email_valido(email):
    """Verifica si el correo tiene un formato válido."""
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, email) is not None

def porcentaje(valor, total):
    """Devuelve el porcentaje sin lanzar división por cero."""
    try:
        if total == 0:
            return 0
        return (valor / total) * 100
    except (TypeError, ZeroDivisionError):
        return 0

def redondear_dos_decimales(valor):
    """Redondea a dos decimales."""
    try:
        return round(float(valor), 2)
    except (ValueError, TypeError):
        return 0
