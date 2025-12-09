import os
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

# -----------------------------
# Estado del inversor (dummy)
# -----------------------------
INVERTER_STATE = {
    "id": "inversor_1",
    "name": "Inversor Solar",
    "online": True,
    "power": 125,      # vatios actuales
    "voltage": 24.3    # voltaje actual
}

# -----------------------------
# Account Linking (OAuth 2.0 Dummy)
# -----------------------------
@app.route("/authorize")
def authorize():
    redirect_uri = request.args.get("redirect_uri")
    state = request.args.get("state")
    if not redirect_uri:
        return "Falta redirect_uri", 400
    # Código de autorización ficticio
    code = "dummy-code"
    # Redirige a Google con code y state
    return redirect(f"{redirect_uri}?code={code}&state={state}")

@app.route("/token", methods=["POST"])
def token():
    # Intercambio code -> access_token dummy
    return jsonify({
        "access_token": "dummy-access-token",
        "token_type": "Bearer",
        "expires_in": 3600
    })

# -----------------------------
# Endpoint principal C2C
# -----------------------------
@app.route("/", methods=["POST"])
def cloud_to_cloud():
    body = request.get_json(silent=True)
    print("BODY RECIBIDO:", body)

    if not body:
        return jsonify({"status": "ok", "message": "Función activa"}), 200

    inputs = body.get("inputs", [])
    if len(inputs) == 0:
        return jsonify({"status": "error", "message": "No hay inputs"}), 400

    intent = inputs[0].get("intent")
    print("Intent detectado:", intent)

    # -----------------------------
    # SYNC
    # -----------------------------
    if intent in ["SYNC", "action.devices.SYNC"]:
        response = {
            "requestId": body.get("requestId", "req-001"),
            "payload": {
                "agentUserId": "user-123",  # ID de usuario ficticio
                "devices": [
                    {
                        "id": INVERTER_STATE["id"],
                        "type": "action.devices.types.ENERGY_SENSOR",
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
        }
        return jsonify(response)

    # -----------------------------
    # QUERY
    # -----------------------------
    elif intent in ["QUERY", "action.devices.QUERY"]:
        devices_query = inputs[0].get("payload", {}).get("devices", [])
        payload_devices = {}
        for dev in devices_query:
            dev_id = dev.get("id")
            if dev_id == INVERTER_STATE["id"]:
                payload_devices[dev_id] = {
                    "online": INVERTER_STATE["online"],
                    "status": "SUCCESS",
                    "currentPower": INVERTER_STATE["power"],
                    "voltage": INVERTER_STATE["voltage"]
                }

        response = {
            "requestId": body.get("requestId", "req-002"),
            "payload": {"devices": payload_devices}
        }
        return jsonify(response)

    # -----------------------------
    # EXECUTE
    # -----------------------------
    elif intent in ["EXECUTE", "action.devices.EXECUTE"]:
        commands = inputs[0].get("payload", {}).get("commands", [])
        results = []
        for cmd in commands:
            devices = cmd.get("devices", [])
            for device in devices:
                device_id = device.get("id")
                results.append({
                    "ids": [device_id],
                    "status": "SUCCESS",
                    "states": INVERTER_STATE
                })
        response = {"requestId": body.get("requestId", "req-003"), "payload": {"commands": results}}
        return jsonify(response)

    # Intent desconocido
    return jsonify({"status": "error", "message": f"Intent desconocido: {intent}"}), 400

# -----------------------------
# Ejecución local
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
