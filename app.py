from flask import Flask, request, jsonify, make_response
from flask_sock import Sock
import uuid
import json
import hashlib
from datetime import datetime, timezone
import graphene

app = Flask(__name__)
sock = Sock(app)

# In-memory "database"
services = {}

# Connected WebSocket clients
ws_clients = set()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def compute_etag(obj: dict) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.md5(raw).hexdigest()


def broadcast(event: dict) -> None:
    msg = json.dumps(event)
    dead = []
    for ws in list(ws_clients):
        try:
            ws.send(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        ws_clients.discard(ws)


# -------------------------
# Health / Debug
# -------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/debug/services")
def debug_services():
    return jsonify(services), 200


# -------------------------
# REST (Versioned) - /api/v1
# -------------------------

@app.post("/api/v1/services")
def create_service():
    data = request.get_json(silent=True) or {}

    required = ["type", "name", "address"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"error": "missing_fields", "fields": missing}), 400

    sid = str(uuid.uuid4())
    service = {
        "id": sid,
        "type": data["type"],
        "name": data["name"],
        "address": data["address"],
        "hours": data.get("hours", ""),
        "phone": data.get("phone", ""),
        "updatedAt": now_iso(),
    }
    services[sid] = service

    # WebSocket event
    broadcast({"event": "serviceCreated", "service": service})

    resp = jsonify(service)
    resp.status_code = 201
    resp.headers["Location"] = f"/api/v1/services/{sid}"
    return resp


@app.get("/api/v1/services")
def list_services():
    t = request.args.get("type")
    items = list(services.values())
    if t:
        items = [s for s in items if s.get("type") == t]
    return jsonify(items), 200


@app.get("/api/v1/services/<sid>")
def get_service(sid):
    service = services.get(sid)
    if not service:
        return jsonify({"error": "not_found"}), 404

    etag = compute_etag(service)
    inm = request.headers.get("If-None-Match")

    # cache headers
    cache_control = "private, max-age=0, must-revalidate"

    if inm and inm == etag:
        resp = make_response("", 304)
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = cache_control
        return resp

    resp = jsonify(service)
    resp.headers["ETag"] = etag
    resp.headers["Cache-Control"] = cache_control
    return resp, 200


@app.put("/api/v1/services/<sid>")
def put_service(sid):
    if sid not in services:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    required = ["type", "name", "address"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"error": "missing_fields", "fields": missing}), 400

    service = services[sid]
    service["type"] = data["type"]
    service["name"] = data["name"]
    service["address"] = data["address"]
    service["hours"] = data.get("hours", "")
    service["phone"] = data.get("phone", "")
    service["updatedAt"] = now_iso()
    services[sid] = service

    return jsonify(service), 200


@app.patch("/api/v1/services/<sid>")
def patch_service(sid):
    service = services.get(sid)
    if not service:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    for k in ["type", "name", "address", "hours", "phone"]:
        if k in data:
            service[k] = data[k]

    service["updatedAt"] = now_iso()
    services[sid] = service
    return jsonify(service), 200


@app.delete("/api/v1/services/<sid>")
def delete_service(sid):
    if sid not in services:
        return jsonify({"error": "not_found"}), 404
    del services[sid]
    return ("", 204)


# -------------------------
# WebSocket - /ws
# -------------------------

@sock.route("/ws")
def ws_endpoint(ws):
    ws_clients.add(ws)
    try:
        ws.send(json.dumps({"event": "connected"}))
        while True:
            msg = ws.receive()
            if msg is None:
                break
    finally:
        ws_clients.discard(ws)


# -------------------------
# GraphQL - /graphql
# -------------------------

class ServiceType(graphene.ObjectType):
    id = graphene.String()
    type = graphene.String()
    name = graphene.String()
    address = graphene.String()
    hours = graphene.String()
    phone = graphene.String()
    updatedAt = graphene.String()


class Query(graphene.ObjectType):
    services = graphene.List(ServiceType, type=graphene.String())
    service = graphene.Field(ServiceType, id=graphene.String(required=True))

    def resolve_services(self, info, type=None):
        items = list(services.values())
        if type:
            items = [s for s in items if s.get("type") == type]
        return items

    def resolve_service(self, info, id):
        return services.get(id)


schema = graphene.Schema(query=Query)


@app.post("/graphql")
def graphql_endpoint():
    body = request.get_json(silent=True) or {}
    query = body.get("query")
    variables = body.get("variables")

    if not query:
        return jsonify({"error": "missing_query"}), 400

    result = schema.execute(query, variable_values=variables)
    payload = {"data": result.data}
    if result.errors:
        payload["errors"] = [str(e) for e in result.errors]
        return jsonify(payload), 400

    return jsonify(payload), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
