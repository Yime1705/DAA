from flask import Blueprint, request, jsonify
from store import store

sections_bp = Blueprint("sections", __name__)


@sections_bp.get("/api/sections")
def get_sections():
    return jsonify(list(store["sections"].values()))


@sections_bp.post("/api/sections")
def add_section():
    data = request.json
    if not data.get("id") or not data.get("name"):
        return jsonify({"error": "Missing id or name"}), 400
    if data["id"] in store["sections"]:
        return jsonify({"error": "Section ID already exists"}), 409

    section = {
        "id": data["id"],
        "name": data["name"],
        "student_count": int(data.get("student_count", 30)),
        "course_ids": data.get("course_ids", []),
    }
    store["sections"][data["id"]] = section
    return jsonify(section), 201


@sections_bp.delete("/api/sections/<sid>")
def delete_section(sid):
    if sid not in store["sections"]:
        return jsonify({"error": "Not found"}), 404
    del store["sections"][sid]
    return jsonify({"ok": True})
