from flask import Flask, request, jsonify, redirect
import threading
import time
import random

app = Flask(__name__)

# -------------------------------------------------------------------
# CACHE PARA DATOS DEL SENSOR
# -------------------------------------------------------------------
CACHE = {"power": 0.0, "voltage": 0.0}
lock = threading.Lock()

# -------------------------------------------------------------------
# GENERADOR DE DATOS CADA 10s
# -------------------------------------------------------------------
def update_sensor_loop():
    while True:
        with lock:
            CACHE["power"] = round(random.uniform(50, 500), 2)
            CACHE["voltage"] = round(random.uniform(20, 30), 2)
        print(f"[SENSOR] Power={CACHE['power']}W  Voltage={CACHE['voltage']}V")
        time.sleep(10)

threading.Thread(target=update_sensor_loop, daemon=True).start()

# -------------------------------------------------------------------
# 1) AUTHORIZATION ENDPOINT (OAuth 2.0)
# Google manda al usuario aquí para login
# -------------------------------------------------------------------
@app.route("/authorize")
def authorize():
    client_id = request.args.get("client_id")
    redirect_uri = request.args.get("redirect_uri")
    state = request.args.get("state")

    # Simula login exitoso
    redirect_url = f"{redirect_uri}?code=12345&state={state}"
    return redirect(redirect_url, code=302)

# -------------------------------------------------------------------
# 2) TOKEN ENDPOINT
# Google intercambia "code" por tokens
# -------------------------------------------------------------------
@app.route("/token", methods=["POST"])
def token():
    grant_type = request.form.get("grant_type")

    if grant_type == "authorization_code":
        return jsonify({
            "token_type": "bearer",
            "access_token": "ACCESS_TOKEN_ABC",
            "refresh_token": "REFRESH_TOKEN_ABC",
            "expires_in": 3600
        })

    elif grant_type == "refresh_token":
        return jsonify({
            "token_type": "bearer",
            "access_token": "ACCESS_TOKEN_REFRESHED",
            "expires_in": 3600
        })

    else:
        return jsonify({"error": "unsupported_grant_type"}), 400


# -------------------------------------------------------------------
# 3) ENDPOINT PRINCIPAL — HANDLER DE INTENTS
# SYNC, QUERY, EXECUTE
# -------------------------------------------------------------------
@app.route("/", methods=["POST"])
def root():
    body = request.get_json()
    print("BODY:", body)

    intent = body["inputs"][0]["intent"]

    # ---------------------------------------------------------------
    # INTENT: SYNC
    # ---------------------------------------------------------------
    if intent == "action.devices.SYNC":
        return jsonify({
            "requestId": body["requestId"],
            "payload": {
                "agentUserId": "usuario_1",
                "devices": [
                    {
                        "id": "inversor_1",
                        "type": "action.devices.types.THERMOSTAT",
                        "traits": [
                            "action.devices.traits.TemperatureSetting"
                        ],
                        "name": {"name": "Inversor Solar"},
                        "willReportState": False,
                        "attributes": {
                            "availableThermostatModes": ["off"],
                            "thermostatTemperatureUnit": "C"
                        }
                    }
                ]
            }
        })

    # ---------------------------------------------------------------
    # INTENT: QUERY
    # Devuelve valores actuales del sensor
    # ---------------------------------------------------------------
    elif intent == "action.devices.QUERY":
        with lock:
            temp = CACHE["power"] / 10      # conversión arbitraria
            target = CACHE["voltage"]       # conversión arbitraria

        return jsonify({
            "requestId": body["requestId"],
            "payload": {
                "devices": {
                    "inversor_1": {
                        "online": True,
                        "thermostatMode": "off",
                        "thermostatTemperatureAmbient": temp,
                        "thermostatTemperatureSetpoint": target
                    }
                }
            }
        })
    # ---------------------------------------------------------------
    # INTENT: EXECUTE
    # Para comandos (aunque tu sensor no tiene comandos)
    # ---------------------------------------------------------------
    elif intent == "action.devices.EXECUTE":
        commands = body["inputs"][0]["payload"]["commands"]

        results = []

        for cmd in commands:
            for device in cmd["devices"]:
                device_id = device["id"]
                exec_cmd = cmd["execution"][0]["command"]

                print(f"[EXECUTE] {device_id}  CMD={exec_cmd}")

                # Respuesta estándar
                results.append({
                    "ids": [device_id],
                    "status": "SUCCESS",
                    "states": {
                        "online": True
                    }
                })

        return jsonify({
            "requestId": body["requestId"],
            "payload": {
                "commands": results
            }
        })

    else:
        return jsonify({"error": f"Intent no soportado: {intent}"}), 400


# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
