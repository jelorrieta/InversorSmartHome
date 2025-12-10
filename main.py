import threading
import time
import random
from flask import Flask, jsonify, request, redirect

app = Flask(__name__)

# -----------------------------
# Estado dinámico del inversor
# -----------------------------
SENSOR_STATE = {"power": 0, "voltage": 0}

# Thread que genera datos aleatorios cada 10 segundos
def sensor_loop():
    while True:
        SENSOR_STATE["power"] = round(random.uniform(100, 150), 1)
        SENSOR_STATE["voltage"] = round(random.uniform(23.5, 24.7), 1)
        print(f"[SENSOR] Power: {SENSOR_STATE['power']} W, Voltage: {SENSOR_STATE['voltage']} V")
        time.sleep(10)

threading.Thread(target=sensor_loop, daemon=True).start()

# -----------------------------
# Account Linking (OAuth 2.0)
# -----------------------------
@app.route("/authorize")
def authorize():
    redirect_uri = request.args.get("redirect_uri")
    state = request.args.get("state")
    if not redirect_uri:
        return "Falta redirect_uri", 400
    code = "dummy-code"
    return redirect(f"{redirect_uri}?code={code}&state={state}")

@app.route("/token", methods=["POST"])
def token():
    return jsonify({
        "access_token": "dummy-access-token",
        "token_type": "Bearer",
        "expires_in": 3600
    })

# -----------------------------
# Endpoint principal
# -----------------------------
@app.route("/", methods=["POST"])
def main_endpoint():
    body = request.get_json(silent=True) or {}
    intent = None
    if "intent" in body:
        intent = body["intent"]
    elif "inputs" in body and len(body["inputs"]) > 0:
        intent = body["inputs"][0].get("intent")

    print("BODY RECIBIDO:", body)
    print("Intent detectado:", intent)

    # SYNC
    if intent in ["SYNC", "action.devices.SYNC"]:
        return jsonify({
            "requestId": body.get("requestId", "req-001"),
            "payload": {
                "devices": [
                    {
                        "id": "inversor_1",
                        "type": "action.devices.types.SENSOR",
                        "traits": ["action.devices.traits.EnergyStorage"],
                        "name": {"name": "Inversor Solar"},
                        "willReportState": False,
                        "deviceInfo": {
                            "manufacturer": "MiEmpresa",
                            "model": "Inversor 3000W",
                            "hwVersion": "1.0",
                            "swVersion": "1.0"
                        }
                    }
                ]
            }
        })

    # QUERY
    elif intent in ["QUERY", "action.devices.QUERY"]:
        return jsonify({
            "requestId": body.get("requestId", "req-002"),
            "payload": {
                "devices": {
                    "inversor_1": {
                        "online": True,
                        "status": "SUCCESS",
                        "currentPower": SENSOR_STATE["power"],
                        "voltage": SENSOR_STATE["voltage"]
                    }
                }
            }
        })

    # EXECUTE
    elif intent in ["EXECUTE", "action.devices.EXECUTE"]:
        commands = body.get("commands", []) or body.get("inputs", [{}])[0].get("payload", {}).get("commands", [])
        results = []
        for cmd in commands:
            devices = cmd.get("devices", [])
            for device in devices:
                device_id = device.get("id")
                # Aquí puedes simular la ejecución de comandos
                results.append({
                    "ids": [device_id],
                    "status": "SUCCESS",
                    "states": SENSOR_STATE
                })
        return jsonify({
            "requestId": body.get("requestId", "req-003"),
            "payload": {"commands": results}
        })

    # Intent desconocido
    return jsonify({"status": "error", "message": f"Intent desconocido: {intent}"}), 400

# -----------------------------
# EJECUCIÓN LOCAL OPCIONAL
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
