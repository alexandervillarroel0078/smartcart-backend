from flask import Blueprint, jsonify
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import json

import requests
from routes.voz.comandos_voz import interpretar_texto  # ✅ importar la función correcta

voz_inteligente_bp = Blueprint('voz_inteligente', __name__)

MODEL_PATH = "C:/Users/Alexader/OneDrive/Desktop/vosk-model-small-es-0.42"
model = Model(MODEL_PATH)
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(f"⚠️ Estado: {status}")
    q.put(bytes(indata))

@voz_inteligente_bp.route('/voz/test/<int:id_usuario>', methods=['GET'])
def escuchar_y_ejecutar(id_usuario):
    samplerate = 16000
    device = None

    try:
        print("🎙️ Escuchando por voz...")
        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device,
                               dtype='int16', channels=1, callback=callback):
            rec = KaldiRecognizer(model, samplerate)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    resultado = json.loads(rec.Result())
                    texto = resultado.get("text", "")
                    print("📝 Reconocido:", texto)

                    # ✅ Paso 1: Interpretar
                    interpretacion = interpretar_texto(texto)

                    # ✅ Paso 2: Ejecutar (POST a /voz/procesar)
                    r = requests.post("http://localhost:5000/voz/procesar", json={
                        "texto": texto,
                        "id_usuario": id_usuario
                    })

                    return jsonify({
                        "texto_reconocido": texto,
                        "accion_detectada": interpretacion,
                        "respuesta": r.json()
                    }), r.status_code

    except Exception as e:
        print(f"❌ Error de micrófono: {str(e)}")
        return jsonify({"error": "No se pudo capturar voz"}), 500



@voz_inteligente_bp.route('/voz/interpretar-directo', methods=['GET'])
def solo_interpretar_por_voz():
    samplerate = 16000
    device = None

    try:
        print("🎧 Solo interpretando voz...")
        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device,
                               dtype='int16', channels=1, callback=callback):
            rec = KaldiRecognizer(model, samplerate)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    resultado = json.loads(rec.Result())
                    texto = resultado.get("text", "")
                    print("📝 Reconocido:", texto)

                    interpretacion = interpretar_texto(texto)
                    return jsonify({
                        "texto_reconocido": texto,
                        "accion_detectada": interpretacion
                    }), 200

    except Exception as e:
        print(f"❌ Error al capturar voz:", e)
        return jsonify({"error": "No se pudo interpretar voz"}), 500
