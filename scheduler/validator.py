from collections import defaultdict


def validate(sessions):
    """Check all hard constraints and return a list of violation strings."""
    errors = []
    slot_teacher = defaultdict(list)
    slot_section = defaultdict(list)
    slot_room = defaultdict(list)

    for s in sessions:
        slot_teacher[(s.color, s.teacher.id)].append(s.id)
        slot_section[(s.color, s.section.id)].append(s.id)
        if s.room:
            slot_room[(s.color, s.room.id)].append(s.id)

    for (slot, tid), sids in slot_teacher.items():
        if len(sids) > 1:
            errors.append(f"Teacher conflict at slot {slot}: sessions {sids}")
    for (slot, sid), sids in slot_section.items():
        if len(sids) > 1:
            errors.append(f"Section conflict at slot {slot}: sessions {sids}")
    for (slot, rid), sids in slot_room.items():
        if len(sids) > 1:
            errors.append(f"Room conflict at slot {slot}: sessions {sids}")

    return errors


def validate_orphans(courses, teachers, sections):
    """Return warning strings for courses with no teacher or no section enrollment."""
    orphans = []

    teacher_by_course = {}
    for t in teachers.values():
        for cid in t.course_ids:
            teacher_by_course[cid] = t

    section_courses = {cid for s in sections.values() for cid in s.course_ids}

    for cid, course in courses.items():
        if cid not in teacher_by_course:
            orphans.append(f"Course '{course.name}' ({cid}) has no teacher assigned.")
        if cid not in section_courses:
            orphans.append(f"Course '{course.name}' ({cid}) is not enrolled in any section.")

    return orphans


def count_conflicts(sessions):
    """Count teacher, section, and room double-bookings across all timeslots."""
    slot_groups = defaultdict(list)
    for s in sessions:
        slot_groups[s.color].append(s)

    conflicts = 0
    for group in slot_groups.values():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                si, sj = group[i], group[j]
                if (
                    si.teacher.id == sj.teacher.id
                    or si.section.id == sj.section.id
                    or (si.room and sj.room and si.room.id == sj.room.id)
                ):
                    conflicts += 1

    return conflicts
