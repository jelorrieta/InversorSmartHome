import os
import random
from flask import Flask, request, jsonify

app = Flask(__name__)

INVERTER_STATE = {
    "id": "inversor_1",
    "name": "Inversor Solar",
    "online": True,
    "power": 0,
    "voltage": 0
}

def update_sensor():
    INVERTER_STATE["power"] = round(random.uniform(100, 150), 1)
    INVERTER_STATE["voltage"] = round(random.uniform(23.5, 24.5), 1)

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

@app.route("/", methods=["POST"])
def main_endpoint():
    update_sensor()
    body = request.get_json(silent=True)
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
                # Aquí podrías procesar comandos reales, por ahora simulamos SUCCESS
                results.append({
                    "ids": [device_id],
                    "status": "SUCCESS",
                    "states": INVERTER_STATE
                })
        return jsonify({
            "requestId": body.get("requestId", "req-003"),
            "payload": {"commands": results}
        })

    # ----------------- INTENT DESCONOCIDO -----------------
    return jsonify({"status": "error", "message": f"Intent desconocido: {intent}"}), 400
