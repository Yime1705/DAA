DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
TIMES = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"]


def get_needed_type(session):
    """Return the room type required for a given session."""
    needed = "lab" if session.course.session_type == "lab" else "classroom"
    if needed == "classroom" and session.section.student_count > 100:
        needed = "lecture_hall"
    return needed
