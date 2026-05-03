"""
GIKI Timetable Scheduler — Flask Backend
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from scheduler import GIKIScheduler

app = Flask(__name__)
CORS(app)

store = {
    "courses": {},
    "teachers": {},
    "rooms": {},
    "sections": {},
    "last_schedule": None,
    "last_stats": None,
}

def build_scheduler():
    s = GIKIScheduler()
    for c in store["courses"].values():
        s.add_course(**c)
    for t in store["teachers"].values():
        s.add_teacher(**t)
    for r in store["rooms"].values():
        s.add_room(**r)
    for sec in store["sections"].values():
        s.add_section(**sec)
    return s

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/courses", methods=["GET"])
def get_courses():
    return jsonify(list(store["courses"].values()))

@app.route("/api/courses", methods=["POST"])
def add_course():
    data = request.json
    for f in ["id", "name", "sessions_per_week", "session_type"]:
        if not data.get(f):
            return jsonify({"error": f"Missing field: {f}"}), 400
    if data["id"] in store["courses"]:
        return jsonify({"error": "Course ID already exists"}), 409
    course = {"id": data["id"], "name": data["name"],
              "sessions_per_week": int(data["sessions_per_week"]),
              "session_type": data["session_type"],
              "duration_slots": int(data.get("duration_slots", 1))}
    store["courses"][data["id"]] = course
    return jsonify(course), 201

@app.route("/api/courses/<cid>", methods=["DELETE"])
def delete_course(cid):
    if cid not in store["courses"]:
        return jsonify({"error": "Not found"}), 404
    del store["courses"][cid]
    return jsonify({"ok": True})

@app.route("/api/teachers", methods=["GET"])
def get_teachers():
    return jsonify(list(store["teachers"].values()))

@app.route("/api/teachers", methods=["POST"])
def add_teacher():
    data = request.json
    if not data.get("id") or not data.get("name"):
        return jsonify({"error": "Missing id or name"}), 400
    if data["id"] in store["teachers"]:
        return jsonify({"error": "Teacher ID already exists"}), 409
    teacher = {"id": data["id"], "name": data["name"],
               "course_ids": data.get("course_ids", []),
               "unavailable_slots": data.get("unavailable_slots", [])}
    store["teachers"][data["id"]] = teacher
    return jsonify(teacher), 201

@app.route("/api/teachers/<tid>", methods=["DELETE"])
def delete_teacher(tid):
    if tid not in store["teachers"]:
        return jsonify({"error": "Not found"}), 404
    del store["teachers"][tid]
    return jsonify({"ok": True})

@app.route("/api/rooms", methods=["GET"])
def get_rooms():
    return jsonify(list(store["rooms"].values()))

@app.route("/api/rooms", methods=["POST"])
def add_room():
    data = request.json
    if not data.get("id") or not data.get("name"):
        return jsonify({"error": "Missing id or name"}), 400
    if data["id"] in store["rooms"]:
        return jsonify({"error": "Room ID already exists"}), 409
    room = {"id": data["id"], "name": data["name"],
            "capacity": int(data.get("capacity", 30)),
            "room_type": data.get("room_type", "classroom")}
    store["rooms"][data["id"]] = room
    return jsonify(room), 201

@app.route("/api/rooms/<rid>", methods=["DELETE"])
def delete_room(rid):
    if rid not in store["rooms"]:
        return jsonify({"error": "Not found"}), 404
    del store["rooms"][rid]
    return jsonify({"ok": True})

@app.route("/api/sections", methods=["GET"])
def get_sections():
    return jsonify(list(store["sections"].values()))

@app.route("/api/sections", methods=["POST"])
def add_section():
    data = request.json
    if not data.get("id") or not data.get("name"):
        return jsonify({"error": "Missing id or name"}), 400
    if data["id"] in store["sections"]:
        return jsonify({"error": "Section ID already exists"}), 409
    section = {"id": data["id"], "name": data["name"],
               "student_count": int(data.get("student_count", 30)),
               "course_ids": data.get("course_ids", [])}
    store["sections"][data["id"]] = section
    return jsonify(section), 201

@app.route("/api/sections/<sid>", methods=["DELETE"])
def delete_section(sid):
    if sid not in store["sections"]:
        return jsonify({"error": "Not found"}), 404
    del store["sections"][sid]
    return jsonify({"ok": True})

@app.route("/api/generate", methods=["POST"])
def generate():
    if not store["courses"]:
        return jsonify({"error": "No courses added"}), 400
    if not store["teachers"]:
        return jsonify({"error": "No teachers added"}), 400
    if not store["sections"]:
        return jsonify({"error": "No sections added"}), 400
    if not store["rooms"]:
        return jsonify({"error": "No rooms added"}), 400
    try:
        scheduler = build_scheduler()
        result = scheduler.generate_schedule()
        errors = scheduler.validate()
        store["last_schedule"] = result["schedule"]
        store["last_stats"] = result["stats"]
        return jsonify({"ok": True, "schedule": result["schedule"],
                        "stats": result["stats"], "validation_errors": errors})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/schedule", methods=["GET"])
def get_schedule():
    if store["last_schedule"] is None:
        return jsonify({"error": "No schedule generated yet"}), 404
    return jsonify({"schedule": store["last_schedule"], "stats": store["last_stats"]})

@app.route("/api/summary", methods=["GET"])
def summary():
    return jsonify({"courses": len(store["courses"]), "teachers": len(store["teachers"]),
                    "rooms": len(store["rooms"]), "sections": len(store["sections"]),
                    "schedule_ready": store["last_schedule"] is not None})

@app.route("/api/reset", methods=["POST"])
def reset():
    store.update({"courses": {}, "teachers": {}, "rooms": {}, "sections": {},
                  "last_schedule": None, "last_stats": None})
    return jsonify({"ok": True})

@app.route("/api/load-demo", methods=["POST"])
def load_demo():
    store["courses"] = {
        "CS301": {"id":"CS301","name":"Data Structures","sessions_per_week":2,"session_type":"lecture","duration_slots":1},
        "CS302": {"id":"CS302","name":"Algorithms","sessions_per_week":2,"session_type":"lecture","duration_slots":1},
        "CS303": {"id":"CS303","name":"Object Oriented Programming","sessions_per_week":2,"session_type":"lecture","duration_slots":1},
        "CS304": {"id":"CS304","name":"OOP Lab","sessions_per_week":1,"session_type":"lab","duration_slots":1},
        "CS305": {"id":"CS305","name":"Database Systems","sessions_per_week":2,"session_type":"lecture","duration_slots":1},
        "CS306": {"id":"CS306","name":"Database Lab","sessions_per_week":1,"session_type":"lab","duration_slots":1},
        "EE301": {"id":"EE301","name":"Circuit Analysis","sessions_per_week":2,"session_type":"lecture","duration_slots":1},
        "EE302": {"id":"EE302","name":"Signals & Systems","sessions_per_week":2,"session_type":"lecture","duration_slots":1},
        "MATH301":{"id":"MATH301","name":"Calculus III","sessions_per_week":3,"session_type":"lecture","duration_slots":1},
        "CS401": {"id":"CS401","name":"Cybersecurity","sessions_per_week":2,"session_type":"lecture","duration_slots":1},
        "CS402": {"id":"CS402","name":"AI & Machine Learning","sessions_per_week":2,"session_type":"lecture","duration_slots":1},
        "CS403": {"id":"CS403","name":"Computer Networks","sessions_per_week":2,"session_type":"lecture","duration_slots":1},
    }
    store["teachers"] = {
        "T001":{"id":"T001","name":"Dr. Ahmed Khan","course_ids":["CS301","CS302"],"unavailable_slots":[]},
        "T002":{"id":"T002","name":"Dr. Sara Malik","course_ids":["CS303","CS304"],"unavailable_slots":[]},
        "T003":{"id":"T003","name":"Prof. Usman Ali","course_ids":["CS305","CS306"],"unavailable_slots":[]},
        "T004":{"id":"T004","name":"Dr. Fatima Zahra","course_ids":["EE301","EE302"],"unavailable_slots":[]},
        "T005":{"id":"T005","name":"Prof. Bilal Rao","course_ids":["MATH301"],"unavailable_slots":[]},
        "T006":{"id":"T006","name":"Dr. Nadia Hussain","course_ids":["CS401","CS402"],"unavailable_slots":[]},
        "T007":{"id":"T007","name":"Dr. Tariq Mehmood","course_ids":["CS403"],"unavailable_slots":[]},
    }
    store["rooms"] = {
        "AHA": {"id":"AHA","name":"AHA Auditorium","capacity":300,"room_type":"lecture_hall"},
        "LH1": {"id":"LH1","name":"Lecture Hall 1","capacity":120,"room_type":"lecture_hall"},
        "LH2": {"id":"LH2","name":"Lecture Hall 2","capacity":120,"room_type":"lecture_hall"},
        "CR1": {"id":"CR1","name":"Classroom A-101","capacity":40,"room_type":"classroom"},
        "CR2": {"id":"CR2","name":"Classroom A-102","capacity":40,"room_type":"classroom"},
        "CR3": {"id":"CR3","name":"Classroom B-201","capacity":50,"room_type":"classroom"},
        "LAB1":{"id":"LAB1","name":"CS Lab 1","capacity":40,"room_type":"lab"},
        "LAB2":{"id":"LAB2","name":"CS Lab 2","capacity":40,"room_type":"lab"},
        "LAB3":{"id":"LAB3","name":"EE Lab","capacity":25,"room_type":"lab"},
    }
    store["sections"] = {
        "CS-3A":{"id":"CS-3A","name":"CS Batch 3 - Section A","student_count":35,"course_ids":["CS301","CS302","CS303","CS304","MATH301"]},
        "CS-3B":{"id":"CS-3B","name":"CS Batch 3 - Section B","student_count":35,"course_ids":["CS301","CS302","CS303","CS304","MATH301"]},
        "CS-4A":{"id":"CS-4A","name":"CS Batch 4 - Section A","student_count":30,"course_ids":["CS305","CS306","CS401","CS402","CS403"]},
        "EE-3A":{"id":"EE-3A","name":"EE Batch 3 - Section A","student_count":40,"course_ids":["EE301","EE302","MATH301"]},
    }
    store["last_schedule"] = None
    store["last_stats"] = None
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
