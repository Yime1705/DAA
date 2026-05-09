from flask import Blueprint, request, jsonify
from store import store

courses_bp = Blueprint("courses", __name__)


@courses_bp.get("/api/courses")
def get_courses():
    return jsonify(list(store["courses"].values()))


@courses_bp.post("/api/courses")
def add_course():
    data = request.json
    for field in ["id", "name", "sessions_per_week", "session_type"]:
        if not data.get(field):
            return jsonify({"error": f"Missing field: {field}"}), 400
    if data["id"] in store["courses"]:
        return jsonify({"error": "Course ID already exists"}), 409

    course = {
        "id": data["id"],
        "name": data["name"],
        "sessions_per_week": int(data["sessions_per_week"]),
        "session_type": data["session_type"],
        "duration_slots": int(data.get("duration_slots", 1)),
    }
    store["courses"][data["id"]] = course
    return jsonify(course), 201


@courses_bp.delete("/api/courses/<cid>")
def delete_course(cid):
    if cid not in store["courses"]:
        return jsonify({"error": "Not found"}), 404
    del store["courses"][cid]
    return jsonify({"ok": True})
