from flask import Flask, request, jsonify
import requests
import os
import threading
import time
import random

app = Flask(__name__)

# Cache compartida con lock
CACHE = {"power": None, "voltage": None}
lock = threading.Lock()

def read_sensor():
    """Simula lectura del inversor."""
    try:
        # Aquí tu lectura real del RS485 / ESP32 / API interna:
        power = round(random.uniform(100, 150), 1)     # Watts
        voltage = round(random.uniform(23.5, 25.0), 1) # Volts

        with lock:
            CACHE["power"] = power
            CACHE["voltage"] = voltage

        print(f"[SENSOR] Power: {power} W, Voltage: {voltage} V")
    except Exception as e:
        print("Error leyendo sensor:", e)

def background_loop():
    """Lee los datos cada 10 segundos sin bloquear el main thread."""
    while True:
        read_sensor()
        time.sleep(10)

# Inicia hilo en segundo plano
threading.Thread(target=background_loop, daemon=True).start()

@app.route("/health")
def health():
    return "OK", 200

@app.route("/", methods=["POST"])
def root():
    body = request.get_json()
    print("BODY:", body)

    intent = body["inputs"][0]["intent"]

    if intent == "action.devices.SYNC":
        return jsonify({
            "requestId": body["requestId"],
            "payload": {
                "agentUserId": "usuario_1",
                "devices": [
                    {
                        "id": "inversor_1",
                        "type": "action.devices.types.SENSOR",
                        "traits": ["action.devices.traits.EnergyStorage"],
                        "name": {"name": "Inversor Solar"},
                        "willReportState": False,
                        "attributes": {
                            "sensorStatesSupported": [
                                {"name": "power", "numericValue": True},
                                {"name": "voltage", "numericValue": True}
                            ]
                        }
                    }
                ]
            }
        })

    elif intent == "action.devices.QUERY":
        with lock:
            power = CACHE["power"]
            voltage = CACHE["voltage"]

        return jsonify({
            "requestId": body["requestId"],
            "payload": {
                "devices": {
                    "inversor_1": {
                        "power": power,
                        "voltage": voltage
                    }
                }
            }
        })

    else:
        return jsonify({"error": "intent no soportado"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
