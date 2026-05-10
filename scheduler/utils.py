DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# Real GIKI slot times (tea break 10:00-10:30, lunch 13:30-14:30 are implicit gaps)
TIMES = ["08:00", "09:00", "10:30", "11:30", "12:30", "14:30", "15:30", "16:30"]


def get_needed_type(session):
    """Return the room type required for a given session."""
    needed = "lab" if session.course.session_type == "lab" else "classroom"
    if needed == "classroom" and session.section.student_count > 100:
        needed = "lecture_hall"
    return needed
