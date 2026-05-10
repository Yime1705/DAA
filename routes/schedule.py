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
    # ── Courses — lectures + labs (FCSE Spring 2026) ─────────────────────────
    store["courses"] = {
        # ── Lectures ──
        "CS112":  {"id":"CS112",  "name":"Programming Fundamentals",    "sessions_per_week":3, "session_type":"lecture", "duration_slots":1},
        "CS232":  {"id":"CS232",  "name":"Data Structures",             "sessions_per_week":3, "session_type":"lecture", "duration_slots":1},
        "CS313":  {"id":"CS313",  "name":"Operating Systems",           "sessions_per_week":3, "session_type":"lecture", "duration_slots":1},
        "CS343":  {"id":"CS343",  "name":"Compiler Construction",       "sessions_per_week":2, "session_type":"lecture", "duration_slots":1},
        "CS378":  {"id":"CS378",  "name":"Software Engineering",        "sessions_per_week":2, "session_type":"lecture", "duration_slots":1},
        "CS392":  {"id":"CS392",  "name":"Theory of Automata",          "sessions_per_week":2, "session_type":"lecture", "duration_slots":1},
        "CS444":  {"id":"CS444",  "name":"Computer Networks",           "sessions_per_week":2, "session_type":"lecture", "duration_slots":1},
        "CS464":  {"id":"CS464",  "name":"Artificial Intelligence",     "sessions_per_week":2, "session_type":"lecture", "duration_slots":1},
        "CE222":  {"id":"CE222",  "name":"Circuit Analysis",            "sessions_per_week":3, "session_type":"lecture", "duration_slots":1},
        "CE313":  {"id":"CE313",  "name":"Digital Logic Design",        "sessions_per_week":3, "session_type":"lecture", "duration_slots":1},
        "CE453":  {"id":"CE453",  "name":"Embedded Systems",            "sessions_per_week":2, "session_type":"lecture", "duration_slots":1},
        "DS351":  {"id":"DS351",  "name":"Database Systems",            "sessions_per_week":2, "session_type":"lecture", "duration_slots":1},
        "DS462":  {"id":"DS462",  "name":"Data Science",                "sessions_per_week":2, "session_type":"lecture", "duration_slots":1},
        "DS471":  {"id":"DS471",  "name":"Big Data Analytics",          "sessions_per_week":2, "session_type":"lecture", "duration_slots":1},
        "CY913":  {"id":"CY913",  "name":"Cybersecurity Fundamentals",  "sessions_per_week":2, "session_type":"lecture", "duration_slots":1},
        "CY921":  {"id":"CY921",  "name":"Network Security",            "sessions_per_week":2, "session_type":"lecture", "duration_slots":1},
        "SE211":  {"id":"SE211",  "name":"Software Engineering II",     "sessions_per_week":2, "session_type":"lecture", "duration_slots":1},
        "SE351":  {"id":"SE351",  "name":"Software Project Management", "sessions_per_week":2, "session_type":"lecture", "duration_slots":1},
        # ── Labs ──
        "CS112L": {"id":"CS112L", "name":"Programming Fundamentals Lab","sessions_per_week":1, "session_type":"lab",     "duration_slots":1},
        "CS232L": {"id":"CS232L", "name":"Data Structures Lab",         "sessions_per_week":1, "session_type":"lab",     "duration_slots":1},
        "CE313L": {"id":"CE313L", "name":"Digital Logic Design Lab",    "sessions_per_week":1, "session_type":"lab",     "duration_slots":1},
        "CE453L": {"id":"CE453L", "name":"Embedded Systems Lab",        "sessions_per_week":1, "session_type":"lab",     "duration_slots":1},
        "DS351L": {"id":"DS351L", "name":"Database Systems Lab",        "sessions_per_week":1, "session_type":"lab",     "duration_slots":1},
        "DS462L": {"id":"DS462L", "name":"Data Science Lab",            "sessions_per_week":1, "session_type":"lab",     "duration_slots":1},
        "CY913L": {"id":"CY913L", "name":"Cybersecurity Lab",           "sessions_per_week":1, "session_type":"lab",     "duration_slots":1},
        "CE222L": {"id":"CE222L", "name":"Circuit Analysis Lab",        "sessions_per_week":1, "session_type":"lab",     "duration_slots":1},
    }

    # ── Teachers ──────────────────────────────────────────────────────────────
    store["teachers"] = {
        "T01": {"id":"T01", "name":"Dr. Omar Bin Saeed",   "course_ids":["CS232","CS232L"],        "unavailable_slots":[]},
        "T02": {"id":"T02", "name":"Dr. Qadeer ul Hassan", "course_ids":["CS313"],                 "unavailable_slots":[]},
        "T03": {"id":"T03", "name":"Prof. Dr. Manzoor",    "course_ids":["DS462","DS462L"],        "unavailable_slots":[]},
        "T04": {"id":"T04", "name":"Dr. M. Salman",        "course_ids":["CY913","CY913L"],        "unavailable_slots":[]},
        "T05": {"id":"T05", "name":"Ahsan Shah",           "course_ids":["CS378"],                 "unavailable_slots":[]},
        "T06": {"id":"T06", "name":"Ahmad Nawaz",          "course_ids":["CE313","CE313L","SE211"], "unavailable_slots":[]},
        "T07": {"id":"T07", "name":"Dr. Memoon Sajid",     "course_ids":["CS392"],                 "unavailable_slots":[]},
        "T08": {"id":"T08", "name":"Dr. Khurram Jadoon",   "course_ids":["DS471"],                 "unavailable_slots":[]},
        "T09": {"id":"T09", "name":"Dr. Zoya",             "course_ids":["CS444"],                 "unavailable_slots":[]},
        "T10": {"id":"T10", "name":"Ms. Laraib Noor",      "course_ids":["CS343"],                 "unavailable_slots":[]},
        "T11": {"id":"T11", "name":"Dr. Farah Saeed",      "course_ids":["DS351","DS351L"],        "unavailable_slots":[]},
        "T12": {"id":"T12", "name":"Dr. Shahab Haider",    "course_ids":["CE453","CE453L","CY921"],"unavailable_slots":[]},
        "T13": {"id":"T13", "name":"Dr. Ayaz Umer",        "course_ids":["CS464"],                 "unavailable_slots":[]},
        "T14": {"id":"T14", "name":"Dr. Ahmar Rashid",     "course_ids":["SE351"],                 "unavailable_slots":[]},
        "T15": {"id":"T15", "name":"Badre Munir",          "course_ids":["CS112","CS112L"],        "unavailable_slots":[]},
        "T16": {"id":"T16", "name":"Dr. Rashid Jillani",   "course_ids":["CE222","CE222L"],        "unavailable_slots":[]},
    }

    # ── Rooms — lecture halls + computer/electronics labs ─────────────────────
    store["rooms"] = {
        # Lecture halls
        "CSLH1":   {"id":"CSLH1",   "name":"CS LH1",        "capacity":120, "room_type":"lecture_hall"},
        "CSLH2":   {"id":"CSLH2",   "name":"CS LH2",        "capacity":120, "room_type":"lecture_hall"},
        "CSLH3":   {"id":"CSLH3",   "name":"CS LH3",        "capacity":120, "room_type":"lecture_hall"},
        "ACBLH4":  {"id":"ACBLH4",  "name":"AcB LH4",       "capacity":80,  "room_type":"lecture_hall"},
        "ACBLH5":  {"id":"ACBLH5",  "name":"AcB LH5",       "capacity":80,  "room_type":"lecture_hall"},
        "ACBLH6":  {"id":"ACBLH6",  "name":"AcB LH6",       "capacity":80,  "room_type":"lecture_hall"},
        "ACBLH8":  {"id":"ACBLH8",  "name":"AcB LH8",       "capacity":80,  "room_type":"lecture_hall"},
        "ACBLH9":  {"id":"ACBLH9",  "name":"AcB LH9",       "capacity":80,  "room_type":"lecture_hall"},
        "ACBMLH2": {"id":"ACBMLH2", "name":"AcB MLH2",      "capacity":55,  "room_type":"classroom"},
        # Computer labs
        "CSLAB1":  {"id":"CSLAB1",  "name":"CS Lab 1",      "capacity":60,  "room_type":"lab"},
        "CSLAB2":  {"id":"CSLAB2",  "name":"CS Lab 2",      "capacity":60,  "room_type":"lab"},
        "CSLAB3":  {"id":"CSLAB3",  "name":"CS Lab 3",      "capacity":60,  "room_type":"lab"},
        # Electronics / embedded lab
        "EELAB1":  {"id":"EELAB1",  "name":"EE Lab 1",      "capacity":60,  "room_type":"lab"},
        "EELAB2":  {"id":"EELAB2",  "name":"EE Lab 2",      "capacity":60,  "room_type":"lab"},
        # Data science / AI lab
        "DSLAB1":  {"id":"DSLAB1",  "name":"DS/AI Lab",     "capacity":60,  "room_type":"lab"},
    }

    # ── Sections: 6 programs × 4 batches, no A/B split ───────────────────────
    store["sections"] = {
        # BS Computer Science
        "CS-4": {"id":"CS-4", "name":"BS CS — Batch 4", "student_count":50,
                 "course_ids":["CS444","CS464","DS471","CY913","SE351","DS462L","CY913L"]},
        "CS-3": {"id":"CS-3", "name":"BS CS — Batch 3", "student_count":55,
                 "course_ids":["CS313","CS343","CS392","DS351","SE211","DS351L"]},
        "CS-2": {"id":"CS-2", "name":"BS CS — Batch 2", "student_count":55,
                 "course_ids":["CS232","CS378","CE222","DS351","CS232L","DS351L"]},
        "CS-1": {"id":"CS-1", "name":"BS CS — Batch 1", "student_count":60,
                 "course_ids":["CS112","CE222","CS392","CS112L","CE222L"]},
        # BS Computer Engineering
        "CE-4": {"id":"CE-4", "name":"BS CE — Batch 4", "student_count":45,
                 "course_ids":["CE453","CS444","DS471","SE351","CE453L"]},
        "CE-3": {"id":"CE-3", "name":"BS CE — Batch 3", "student_count":50,
                 "course_ids":["CE313","CE453","CS444","DS351","CE313L","CE453L"]},
        "CE-2": {"id":"CE-2", "name":"BS CE — Batch 2", "student_count":50,
                 "course_ids":["CE222","CE313","CS232","CS392","CE313L","CE222L"]},
        "CE-1": {"id":"CE-1", "name":"BS CE — Batch 1", "student_count":55,
                 "course_ids":["CS112","CE222","CS112L","CE222L"]},
        # BS Artificial Intelligence
        "AI-4": {"id":"AI-4", "name":"BS AI — Batch 4", "student_count":40,
                 "course_ids":["CS464","DS471","CY913","SE351","DS462L"]},
        "AI-3": {"id":"AI-3", "name":"BS AI — Batch 3", "student_count":45,
                 "course_ids":["CS464","DS462","DS471","CS343","DS462L"]},
        "AI-2": {"id":"AI-2", "name":"BS AI — Batch 2", "student_count":45,
                 "course_ids":["CS232","CS392","DS351","CS343","CS232L","DS351L"]},
        "AI-1": {"id":"AI-1", "name":"BS AI — Batch 1", "student_count":50,
                 "course_ids":["CS112","CE222","CS392","CS112L"]},
        # BS Cybersecurity
        "CYS-4": {"id":"CYS-4", "name":"BS CYS — Batch 4", "student_count":35,
                  "course_ids":["CY913","CY921","CS444","DS471","CY913L"]},
        "CYS-3": {"id":"CYS-3", "name":"BS CYS — Batch 3", "student_count":38,
                  "course_ids":["CY913","CY921","CE453","CS444","CY913L","CE453L"]},
        "CYS-2": {"id":"CYS-2", "name":"BS CYS — Batch 2", "student_count":40,
                  "course_ids":["CS232","CE222","CS392","CY913","CY913L","CS232L"]},
        "CYS-1": {"id":"CYS-1", "name":"BS CYS — Batch 1", "student_count":45,
                  "course_ids":["CS112","CE222","CS392","CS112L","CE222L"]},
        # BS Data Science
        "DS-4": {"id":"DS-4", "name":"BS DS — Batch 4", "student_count":35,
                 "course_ids":["DS462","DS471","CS464","SE351","DS462L"]},
        "DS-3": {"id":"DS-3", "name":"BS DS — Batch 3", "student_count":38,
                 "course_ids":["DS462","DS471","CS464","DS351","DS462L","DS351L"]},
        "DS-2": {"id":"DS-2", "name":"BS DS — Batch 2", "student_count":40,
                 "course_ids":["CS232","DS351","CS392","CS343","CS232L","DS351L"]},
        "DS-1": {"id":"DS-1", "name":"BS DS — Batch 1", "student_count":45,
                 "course_ids":["CS112","CE222","DS351","CS112L","CE222L"]},
        # BS Software Engineering
        "SE-4": {"id":"SE-4", "name":"BS SE — Batch 4", "student_count":40,
                 "course_ids":["CS378","SE211","SE351","CS444","DS351L"]},
        "SE-3": {"id":"SE-3", "name":"BS SE — Batch 3", "student_count":45,
                 "course_ids":["CS378","SE211","SE351","DS351","CS343","DS351L"]},
        "SE-2": {"id":"SE-2", "name":"BS SE — Batch 2", "student_count":45,
                 "course_ids":["CS232","CS378","CE222","CS392","CS232L","CE222L"]},
        "SE-1": {"id":"SE-1", "name":"BS SE — Batch 1", "student_count":50,
                 "course_ids":["CS112","CE222","CS392","CS112L","CE222L"]},
    }

    store["last_schedule"] = None
    store["last_stats"] = None
    return jsonify({"ok": True})
