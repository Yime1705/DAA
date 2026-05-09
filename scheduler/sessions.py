from .models import Session


def generate_sessions(courses, teachers, sections):
    """Create one Session per required weekly class occurrence."""
    sessions = []
    sid = 0

    teacher_by_course = {}
    for t in teachers.values():
        for cid in t.course_ids:
            teacher_by_course[cid] = t

    for section in sections.values():
        for cid in section.course_ids:
            course = courses.get(cid)
            if not course:
                continue
            teacher = teacher_by_course.get(cid)
            if not teacher:
                continue
            for _ in range(course.sessions_per_week):
                sessions.append(Session(
                    id=sid,
                    course=course,
                    teacher=teacher,
                    section=section,
                ))
                sid += 1

    return sessions


def build_conflict_graph(sessions):
    """Build adjacency sets: edge if two sessions share a teacher or section."""
    n = len(sessions)
    graph = {i: set() for i in range(n)}

    for i in range(n):
        for j in range(i + 1, n):
            si, sj = sessions[i], sessions[j]
            if si.teacher.id == sj.teacher.id or si.section.id == sj.section.id:
                graph[i].add(j)
                graph[j].add(i)

    return graph
