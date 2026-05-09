from flask import Blueprint, request, jsonify
from store import store

teachers_bp = Blueprint("teachers", __name__)


@teachers_bp.get("/api/teachers")
def get_teachers():
    return jsonify(list(store["teachers"].values()))


@teachers_bp.post("/api/teachers")
def add_teacher():
    data = request.json
    if not data.get("id") or not data.get("name"):
        return jsonify({"error": "Missing id or name"}), 400
    if data["id"] in store["teachers"]:
        return jsonify({"error": "Teacher ID already exists"}), 409

    teacher = {
        "id": data["id"],
        "name": data["name"],
        "course_ids": data.get("course_ids", []),
        "unavailable_slots": data.get("unavailable_slots", []),
    }
    store["teachers"][data["id"]] = teacher
    return jsonify(teacher), 201


@teachers_bp.delete("/api/teachers/<tid>")
def delete_teacher(tid):
    if tid not in store["teachers"]:
        return jsonify({"error": "Not found"}), 404
    del store["teachers"][tid]
    return jsonify({"ok": True})
