import os
import logging
from flask import Flask, request, jsonify, redirect

# Configurar logging para Cloud Run
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Estado dinámico del inversor
INVERTER_STATE = {
    "id": "inversor_1",
    "name": "Inversor Solar",
    "online": True,
    "power": 125,
    "voltage": 24.3
}

# -----------------------------
# Account Linking (OAuth 2.0)
# -----------------------------
@app.route("/authorize")
def authorize():
    redirect_uri = request.args.get("redirect_uri")
    state = request.args.get("state")
    if not redirect_uri:
        return "Falta redirect_uri", 400
    # Código de autorización ficticio
    code = "dummy-code"
    logger.info(f"Redirigiendo a {redirect_uri} con code={code} y state={state}")
    return redirect(f"{redirect_uri}?code={code}&state={state}")

@app.route("/token", methods=["POST"])
def token():
    logger.info("Solicitud de token recibida")
    return jsonify({
        "access_token": "dummy-access-token",
        "token_type": "Bearer",
        "expires_in": 3600
    })

# -----------------------------
# Endpoint principal
# -----------------------------
@app.route("/", methods=["POST", "GET"])
def main_endpoint():
    body = request.get_json(silent=True)
    logger.info(f"BODY RECIBIDO: {body}")

    # Respuesta simple si no hay body
    if not body:
        return jsonify({"status": "ok", "message": "Función activa"}), 200

    # Detectar intent
    intent = None
    if "intent" in body:
        intent = body["intent"]
    elif "inputs" in body and len(body["inputs"]) > 0:
        intent = body["inputs"][0].get("intent")

    logger.info(f"Intent detectado: {intent}")

    # -----------------------------
    # SYNC
    # -----------------------------
    if intent in ["SYNC", "action.devices.SYNC"]:
        response = {
            "requestId": body.get("requestId", "req-001"),
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
    # QUERY
    # -----------------------------
    elif intent in ["QUERY", "action.devices.QUERY"]:
        response = {
            "requestId": body.get("requestId", "req-002"),
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
    # EXECUTE
    # -----------------------------
    elif intent in ["EXECUTE", "action.devices.EXECUTE"]:
        commands = body.get("commands", []) or \
                   body.get("inputs", [{}])[0].get("payload", {}).get("commands", [])
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
# Ejecutar localmente (opcional)
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
