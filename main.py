import functions_framework
from flask import jsonify, request

# Estado dinámico de tu inversor (puede venir de otra fuente)
INVERTER_STATE = {
    "id": "inversor_1",
    "name": "Inversor Solar",
    "online": True,
    "power": 125,    # Valor dinámico
    "voltage": 24.3  # Valor dinámico
}

@functions_framework.http
def main(request):
    body = request.get_json()
    if not body or "intent" not in body:
        return jsonify({"status": "error", "message": "No se recibió 'intent'"}), 400

    intent = body["intent"]

    # ------------------------
    # SYNC → Google pide lista de dispositivos
    # ------------------------
    if intent == "SYNC":
        response = {
            "requestId": body.get("requestId"),
            "payload": {
                "devices": [
                    {
                        "id": INVERTER_STATE["id"],
                        "type": "action.devices.types.ENERGY_SENSOR",
                        "traits": [
                            "action.devices.traits.EnergyStorage"
                        ],
                        "name": {
                            "name": INVERTER_STATE["name"]
                        },
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

    # ------------------------
    # QUERY → Google pide estado actual
    # ------------------------
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

    # ------------------------
    # EXECUTE → Google envía comandos
    # ------------------------
    elif intent == "EXECUTE":
        # Aquí solo simulamos la ejecución
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
        response = {
            "requestId": body.get("requestId"),
            "payload": {
                "commands": results
            }
        }
        return jsonify(response)

    else:
        return jsonify({"status": "error", "message": f"Intent desconocido: {intent}"}), 400
