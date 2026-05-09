from flask import Blueprint, request, jsonify
from store import store

rooms_bp = Blueprint("rooms", __name__)


@rooms_bp.get("/api/rooms")
def get_rooms():
    return jsonify(list(store["rooms"].values()))


@rooms_bp.post("/api/rooms")
def add_room():
    data = request.json
    if not data.get("id") or not data.get("name"):
        return jsonify({"error": "Missing id or name"}), 400
    if data["id"] in store["rooms"]:
        return jsonify({"error": "Room ID already exists"}), 409

    room = {
        "id": data["id"],
        "name": data["name"],
        "capacity": int(data.get("capacity", 30)),
        "room_type": data.get("room_type", "classroom"),
    }
    store["rooms"][data["id"]] = room
    return jsonify(room), 201


@rooms_bp.delete("/api/rooms/<rid>")
def delete_room(rid):
    if rid not in store["rooms"]:
        return jsonify({"error": "Not found"}), 404
    del store["rooms"][rid]
    return jsonify({"ok": True})
