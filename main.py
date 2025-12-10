import os
import random
import threading
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Estado del inversor
INVERTER_STATE = {
    "id": "inversor_1",
    "name": "Inversor Solar",
    "online": True,
    "power": 0,
    "voltage": 0
}

# -------------------------
# Función para actualizar valores cada 10 segundos
# -------------------------
def sensor_loop():
    while True:
        INVERTER_STATE["power"] = round(random.uniform(100, 150), 1)
        INVERTER_STATE["voltage"] = round(random.uniform(23.5, 24.5), 1)
        print(f"[SENSOR] Power: {INVERTER_STATE['power']} W, Voltage: {INVERTER_STATE['voltage']} V")
        time.sleep(10)

# Lanzar el hilo al iniciar la app
threading.Thread(target=sensor_loop, daemon=True).start()

# -------------------------
# Endpoints OAuth (dummy)
# -------------------------
@app.route("/authorize")
def authorize():
    redirect_uri = request.args.get("redirect_uri")
    state = request.args.get("state")
    code = "dummy-code"
    return jsonify({"redirect": f"{redirect_uri}?code={code}&state={state}"})

@app.route("/token", methods=["POST"])
def token():
    return jsonify({
        "access_token": "dummy-access-token",
        "token_type": "Bearer",
        "expires_in": 3600
    })

# -------------------------
# Endpoint principal
# -------------------------
@app.route("/", methods=["POST"])
def main_endpoint():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"status": "ok", "message": "Función activa"}), 200

    intent = None
    if "inputs" in body and len(body["inputs"]) > 0:
        intent = body["inputs"][0].get("intent")

    # ----------------- SYNC -----------------
    if intent in ["SYNC", "action.devices.SYNC"]:
        return jsonify({
            "requestId": body.get("requestId", "req-001"),
            "payload": {
                "devices": [
                    {
                        "id": INVERTER_STATE["id"],
                        "type": "action.devices.types.SENSOR",
                        "traits": ["action.devices.traits.EnergyStorage"],
                        "name": {"name": INVERTER_STATE["name"]},
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

    # ----------------- QUERY -----------------
    elif intent in ["QUERY", "action.devices.QUERY"]:
        devices = {}
        for dev in body["inputs"][0].get("payload", {}).get("devices", []):
            if dev["id"] == INVERTER_STATE["id"]:
                devices[INVERTER_STATE["id"]] = {
                    "online": INVERTER_STATE["online"],
                    "status": "SUCCESS",
                    "currentPower": INVERTER_STATE["power"],
                    "voltage": INVERTER_STATE["voltage"]
                }
        return jsonify({
            "requestId": body.get("requestId", "req-002"),
            "payload": {"devices": devices}
        })

    # ----------------- EXECUTE -----------------
    elif intent in ["EXECUTE", "action.devices.EXECUTE"]:
        results = []
        commands = body["inputs"][0].get("payload", {}).get("commands", [])
        for cmd in commands:
            for device in cmd.get("devices", []):
                device_id = device.get("id")
                results.append({
                    "ids": [device_id],
                    "status": "SUCCESS",
                    "states": INVERTER_STATE
                })
        return jsonify({
            "requestId": body.get("requestId", "req-003"),
            "payload": {"commands": results}
        })

    return jsonify({"status": "error", "message": f"Intent desconocido: {intent}"}), 400

# -------------------------
# Para desarrollo local
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
