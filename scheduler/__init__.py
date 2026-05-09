from .models import Course, Teacher, Room, Section, TimeSlot, Session
from .utils import DAYS, TIMES
from .sessions import generate_sessions, build_conflict_graph
from .dsatur import run_dsatur
from .kempe import run_kempe_optimize
from .rooms import assign_rooms
from .validator import validate, validate_orphans, count_conflicts


class GIKIScheduler:
    def __init__(self):
        self.courses: dict[str, Course] = {}
        self.teachers: dict[str, Teacher] = {}
        self.rooms: dict[str, Room] = {}
        self.sections: dict[str, Section] = {}
        self.sessions: list[Session] = []
        self.timeslots: list[TimeSlot] = self._build_timeslots()
        self.conflict_graph: dict[int, set] = {}
        self.schedule_result: list[dict] = []

    def _build_timeslots(self):
        slots = []
        for idx, (day, time) in enumerate(
            (d, t) for d in DAYS for t in TIMES
        ):
            slots.append(TimeSlot(id=idx, day=day, time=time, display=f"{day} {time}"))
        return slots

    # ── Data ingestion ──────────────────────────────────────────────────────────

    def add_course(self, id, name, sessions_per_week, session_type, duration_slots=1):
        self.courses[id] = Course(id, name, sessions_per_week, session_type, duration_slots)

    def add_teacher(self, id, name, course_ids, unavailable_slots=None):
        self.teachers[id] = Teacher(id, name, course_ids, unavailable_slots or [])

    def add_room(self, id, name, capacity, room_type):
        self.rooms[id] = Room(id, name, capacity, room_type)

    def add_section(self, id, name, student_count, course_ids):
        self.sections[id] = Section(id, name, student_count, course_ids)

    # ── Main entry point ────────────────────────────────────────────────────────

    def generate_schedule(self):
        orphans = validate_orphans(self.courses, self.teachers, self.sections)

        self.sessions = generate_sessions(self.courses, self.teachers, self.sections)
        self.conflict_graph = build_conflict_graph(self.sessions)

        run_dsatur(self.sessions, self.conflict_graph, self.timeslots, self.rooms)
        final_penalty = run_kempe_optimize(
            self.sessions, self.conflict_graph, self.timeslots, iterations=400
        )
        assign_rooms(self.sessions, self.rooms)

        results = []
        for s in self.sessions:
            if s.color < 0:
                continue
            ts = self.timeslots[s.color]
            results.append({
                "session_id": s.id,
                "course_id": s.course.id,
                "course_name": s.course.name,
                "session_type": s.course.session_type,
                "teacher_id": s.teacher.id,
                "teacher_name": s.teacher.name,
                "section_id": s.section.id,
                "section_name": s.section.name,
                "room_id": s.room.id if s.room else None,
                "room_name": s.room.name if s.room else "TBD",
                "room_capacity": s.room.capacity if s.room else 0,
                "day": ts.day,
                "time": ts.time,
                "slot_id": ts.id,
                "display": ts.display,
            })

        self.schedule_result = results
        days_used = len({r["day"] for r in results})
        slots_used = len({r["slot_id"] for r in results})

        return {
            "schedule": results,
            "stats": {
                "total_sessions": len(results),
                "sessions_scheduled": len(results),
                "colors_used": slots_used,
                "hard_conflicts": count_conflicts(self.sessions),
                "days_used": days_used,
                "soft_penalty": final_penalty,
                "orphaned_courses": orphans,
            },
        }

    def validate(self):
        return validate(self.sessions)
