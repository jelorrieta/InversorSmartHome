from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

# -----------------------------
# Estado dinámico del inversor
# -----------------------------
INVERTER_STATE = {
    "id": "inversor_1",
    "name": "Inversor Solar",
    "online": True,
    "power": 125,
    "voltage": 24.3
}

# -----------------------------
# ENDPOINT PARA ACCOUNT LINKING
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
    # Token ficticio
    return jsonify({
        "access_token": "dummy-access-token",
        "token_type": "Bearer",
        "expires_in": 3600
    })

# -----------------------------
# ENDPOINT PRINCIPAL DE DISPOSITIVO
# -----------------------------
@app.route("/", methods=["POST", "GET"])
def main():
    # Intent de debug: ver body recibido
    body = request.get_json(silent=True)
    print("BODY RECIBIDO:", body)

    if not body or "intent" not in body:
        return jsonify({"status": "ok", "message": "Función activa"}), 200

    intent = body["intent"]

    # -----------------------------
    # SYNC: devuelve dispositivos
    # -----------------------------
    if intent == "SYNC":
        response = {
            "requestId": body.get("requestId"),
            "payload": {
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
    # QUERY: devuelve estado del dispositivo
    # -----------------------------
    elif intent == "QUERY":
        response = {
            "requestId": body.get("requestId"),
            "payload": {
                "devices": {
                    INVERTER_STATE["id"]: {
                        "online": INVERTER_STATE["online"],
                        "status": "SUCCESS",
                        "currentPower": INVERTER_STATE["power"],
                        "voltage": INVERTER_STATE["voltage"]
                    }
                }
            }
        }
        return jsonify(response)

    # -----------------------------
    # EXECUTE: ejecutar comandos (simulado)
    # -----------------------------
    elif intent == "EXECUTE":
        commands = body.get("commands", [])
        results = []
        for cmd in commands:
            devices = cmd.get("devices", [])
            for device in devices:
                device_id = device["id"]
                results.append({
                    "ids": [device_id],
                    "status": "SUCCESS",
                    "states": INVERTER_STATE
                })
        response = {"requestId": body.get("requestId"), "payload": {"commands": results}}
        return jsonify(response)

    # Intent desconocido
    return jsonify({"status": "error", "message": f"Intent desconocido: {intent}"}), 400

# -----------------------------
# EJECUCIÓN LOCAL (opcional)
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

