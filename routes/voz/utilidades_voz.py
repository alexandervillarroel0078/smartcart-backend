# 📁 smart_cart_backend/routes/voz/utilidades_voz.py
from word2number import w2n

def convertir_numeros_en_texto(texto):
    palabras = texto.split()
    resultado = []
    for palabra in palabras:
        try:
            numero = str(w2n.word_to_num(palabra))
            resultado.append(numero)
        except:
            resultado.append(palabra)
    return ' '.join(resultado)
