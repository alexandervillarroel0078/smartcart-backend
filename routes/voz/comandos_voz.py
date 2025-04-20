from flask import Blueprint, request, jsonify

comandos_voz_bp = Blueprint('comandos_voz', __name__)

# (Este endpoint es opcional, para probar desde Postman)
@comandos_voz_bp.route('/voz/interpretar', methods=['POST'])
def interpretar_comando():
    data = request.get_json()
    texto = data.get('texto', '').lower().strip()
    resultado = interpretar_texto(texto)
    return jsonify(resultado), 200

# Esta es la función que se usará desde voz_inteligente.py
def interpretar_texto(texto):
    texto = texto.lower().strip()

    if any(p in texto for p in ["agregar", "añadir", "mete"]):
        producto = extraer_producto(texto)
        return {"accion": "agregar", "producto": producto}

    elif any(p in texto for p in ["quitar", "eliminar", "sacar"]):
        producto = extraer_producto(texto)
        return {"accion": "quitar", "producto": producto}

    elif any(p in texto for p in ["aumentar", "subir"]):
        producto = extraer_producto(texto)
        return {"accion": "aumentar", "producto": producto}

    elif any(p in texto for p in ["disminuir", "bajar"]):
        producto = extraer_producto(texto)
        return {"accion": "disminuir", "producto": producto}

    elif "total" in texto or "calcular" in texto:
        return {"accion": "calcular_total"}

    elif "pagar" in texto:
        return {"accion": "pagar"}

    elif "carrito" in texto and any(p in texto for p in ["mostrar", "ver"]):
        return {"accion": "ver_carrito"}

    return {"accion": "no_identificada", "mensaje": texto}


def extraer_producto(texto):
    palabras_excluir = {"el", "la", "los", "las", "al", "a", "del", "carrito", "por", "favor", "una", "un", "y", "de", "se", "quiero", "deseo", "me", "gustaría"}
    palabras = texto.split()
    palabras_filtradas = [p for p in palabras if p not in palabras_excluir]

    for i, palabra in enumerate(palabras_filtradas):
        if palabra in ["agregar", "añadir", "mete", "quitar", "eliminar", "sacar", "aumentar", "subir", "disminuir", "bajar"]:
            return ' '.join(palabras_filtradas[i+1:]).strip()
    return ""
