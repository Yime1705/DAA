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
                        "stats": result["stats"], "validation_errors": errors,
                        "orphaned_courses": result["stats"].get("orphaned_courses", [])})
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
    import random
    
    course_names = [
        ("CS101", "Intro to Computing"), ("CS201", "Programming Fundamentals"),
        ("CS301", "Data Structures"), ("CS302", "Algorithms"),
        ("CS303", "Object Oriented Programming"), ("CS304", "OOP Lab"),
        ("CS305", "Database Systems"), ("CS306", "Database Lab"),
        ("CS401", "Cybersecurity"), ("CS402", "AI & Machine Learning"),
        ("CS403", "Computer Networks"), ("CS404", "Software Engineering"),
        ("EE101", "Circuit Analysis"), ("EE201", "Digital Logic Design"),
        ("MATH101", "Calculus I"), ("MATH201", "Linear Algebra"),
        ("HUM101", "Islamic Studies"), ("HUM102", "Pakistan Studies")
    ]
    
    teacher_names = [
        "Dr. Ahmed Khan", "Dr. Sara Malik", "Prof. Usman Ali", 
        "Dr. Fatima Zahra", "Prof. Bilal Rao", "Dr. Nadia Hussain", 
        "Dr. Tariq Mehmood", "Dr. Zeeshan Haider", "Prof. Maryam Bibi"
    ]
    
    room_data = [
        ("AHA", "AHA Auditorium", 300, "lecture_hall"),
        ("LH1", "Lecture Hall 1", 120, "lecture_hall"),
        ("LH2", "Lecture Hall 2", 120, "lecture_hall"),
        ("CR1", "Classroom A-101", 40, "classroom"),
        ("CR2", "Classroom A-102", 40, "classroom"),
        ("CR3", "Classroom B-201", 50, "classroom"),
        ("LAB1", "CS Lab 1", 40, "lab"),
        ("LAB2", "CS Lab 2", 40, "lab"),
        ("LAB3", "EE Lab", 30, "lab")
    ]
    
    sections_list = [
        ("CS-1A", 40), ("CS-1B", 40), ("CS-3A", 35), ("CS-3B", 35),
        ("EE-1A", 45), ("MATH-1", 50)
    ]

    # Randomly select a subset of courses
    selected_courses = random.sample(course_names, k=min(10, len(course_names)))
    
    store["courses"] = {}
    for cid, name in selected_courses:
        is_lab = "Lab" in name
        store["courses"][cid] = {
            "id": cid, "name": name, 
            "sessions_per_week": 1 if is_lab else random.randint(2, 3),
            "session_type": "lab" if is_lab else "lecture",
            "duration_slots": 1
        }
    
    store["teachers"] = {}
    shuffled_course_ids = list(store["courses"].keys())
    random.shuffle(shuffled_course_ids)
    
    # Distribute courses among teachers
    for i, tname in enumerate(teacher_names):
        tid = f"T{i+1:03d}"
        # Each teacher gets 1-2 courses
        start = (i * 2) % len(shuffled_course_ids)
        assigned = shuffled_course_ids[start:start+2]
        if assigned:
            store["teachers"][tid] = {
                "id": tid, "name": tname, 
                "course_ids": assigned, 
                "unavailable_slots": []
            }
    
    store["rooms"] = {}
    for rid, rname, cap, rtype in room_data:
        store["rooms"][rid] = {"id": rid, "name": rname, "capacity": cap, "room_type": rtype}
        
    store["sections"] = {}
    for sid, scount in sections_list:
        # Assign 3-4 random courses to each section
        store["sections"][sid] = {
            "id": sid, "name": f"Batch {sid}", 
            "student_count": scount, 
            "course_ids": random.sample(list(store["courses"].keys()), k=3)
        }
        
    store["last_schedule"] = None
    store["last_stats"] = None
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
