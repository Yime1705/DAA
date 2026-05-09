from collections import defaultdict
from .utils import get_needed_type


def assign_rooms(sessions, rooms):
    """
    Greedily assign the smallest suitable room to each session.
    Rooms are matched by type (lab/classroom/lecture_hall) and capacity,
    and each room can only be used once per timeslot.
    """
    slot_room_usage = defaultdict(set)

    for session in sessions:
        if session.color < 0:
            continue

        slot = session.color
        needed_type = get_needed_type(session)

        for room in sorted(rooms.values(), key=lambda r: r.capacity):
            if room.id in slot_room_usage[slot]:
                continue

            type_ok = (
                room.room_type == needed_type
                or (needed_type == "classroom" and room.room_type == "lecture_hall")
            )
            cap_ok = room.capacity >= session.section.student_count

            if type_ok and cap_ok:
                session.room = room
                slot_room_usage[slot].add(room.id)
                break
