import random
from flask import Blueprint, request, jsonify
from store import store
from scheduler import GIKIScheduler

schedule_bp = Blueprint("schedule", __name__)


def _build_scheduler():
    """Populate a fresh GIKIScheduler from the current store."""
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


@schedule_bp.post("/api/generate")
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
        scheduler = _build_scheduler()
        result = scheduler.generate_schedule()
        errors = scheduler.validate()
        store["last_schedule"] = result["schedule"]
        store["last_stats"] = result["stats"]
        return jsonify({
            "ok": True,
            "schedule": result["schedule"],
            "stats": result["stats"],
            "validation_errors": errors,
            "orphaned_courses": result["stats"].get("orphaned_courses", []),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@schedule_bp.get("/api/schedule")
def get_schedule():
    if store["last_schedule"] is None:
        return jsonify({"error": "No schedule generated yet"}), 404
    return jsonify({"schedule": store["last_schedule"], "stats": store["last_stats"]})


@schedule_bp.get("/api/summary")
def summary():
    return jsonify({
        "courses": len(store["courses"]),
        "teachers": len(store["teachers"]),
        "rooms": len(store["rooms"]),
        "sections": len(store["sections"]),
        "schedule_ready": store["last_schedule"] is not None,
    })


@schedule_bp.post("/api/reset")
def reset():
    store.update({
        "courses": {}, "teachers": {}, "rooms": {}, "sections": {},
        "last_schedule": None, "last_stats": None,
    })
    return jsonify({"ok": True})


@schedule_bp.post("/api/load-demo")
def load_demo():
    course_names = [
        ("CS101", "Intro to Computing"), ("CS201", "Programming Fundamentals"),
        ("CS301", "Data Structures"), ("CS302", "Algorithms"),
        ("CS303", "Object Oriented Programming"), ("CS304", "OOP Lab"),
        ("CS305", "Database Systems"), ("CS306", "Database Lab"),
        ("CS401", "Cybersecurity"), ("CS402", "AI & Machine Learning"),
        ("CS403", "Computer Networks"), ("CS404", "Software Engineering"),
        ("EE101", "Circuit Analysis"), ("EE201", "Digital Logic Design"),
        ("MATH101", "Calculus I"), ("MATH201", "Linear Algebra"),
        ("HUM101", "Islamic Studies"), ("HUM102", "Pakistan Studies"),
    ]
    teacher_names = [
        "Dr. Ahmed Khan", "Dr. Sara Malik", "Prof. Usman Ali",
        "Dr. Fatima Zahra", "Prof. Bilal Rao", "Dr. Nadia Hussain",
        "Dr. Tariq Mehmood", "Dr. Zeeshan Haider", "Prof. Maryam Bibi",
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
        ("LAB3", "EE Lab", 30, "lab"),
    ]
    sections_list = [
        ("CS-1A", 40), ("CS-1B", 40), ("CS-3A", 35),
        ("CS-3B", 35), ("EE-1A", 45), ("MATH-1", 50),
    ]

    selected_courses = random.sample(course_names, k=min(10, len(course_names)))
    store["courses"] = {}
    for cid, name in selected_courses:
        is_lab = "Lab" in name
        store["courses"][cid] = {
            "id": cid, "name": name,
            "sessions_per_week": 1 if is_lab else random.randint(2, 3),
            "session_type": "lab" if is_lab else "lecture",
            "duration_slots": 1,
        }

    shuffled_ids = list(store["courses"].keys())
    random.shuffle(shuffled_ids)
    store["teachers"] = {}
    for i, tname in enumerate(teacher_names):
        tid = f"T{i+1:03d}"
        start = (i * 2) % len(shuffled_ids)
        assigned = shuffled_ids[start:start + 2]
        if assigned:
            store["teachers"][tid] = {
                "id": tid, "name": tname,
                "course_ids": assigned,
                "unavailable_slots": [],
            }

    store["rooms"] = {}
    for rid, rname, cap, rtype in room_data:
        store["rooms"][rid] = {"id": rid, "name": rname, "capacity": cap, "room_type": rtype}

    store["sections"] = {}
    for sid, scount in sections_list:
        store["sections"][sid] = {
            "id": sid, "name": f"Batch {sid}",
            "student_count": scount,
            "course_ids": random.sample(list(store["courses"].keys()), k=3),
        }

    store["last_schedule"] = None
    store["last_stats"] = None
    return jsonify({"ok": True})
