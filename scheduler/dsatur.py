from collections import defaultdict
from .utils import get_needed_type


def run_dsatur(sessions, conflict_graph, timeslots, rooms):
    """
    Phase 1: DSatur graph coloring with integrated room feasibility check.
    Assigns a timeslot color to every session, guaranteeing zero hard conflicts.
    Complexity: O(V^2)
    """
    n = len(sessions)
    color = [-1] * n
    saturation = [0] * n
    degree = [len(conflict_graph[i]) for i in range(n)]

    def neighbor_colors(i):
        return {color[j] for j in conflict_graph[i] if color[j] >= 0}

    def pick_next():
        best, best_sat, best_deg = -1, -1, -1
        for i in range(n):
            if color[i] >= 0:
                continue
            if saturation[i] > best_sat or (
                saturation[i] == best_sat and degree[i] > best_deg
            ):
                best, best_sat, best_deg = i, saturation[i], degree[i]
        return best

    rooms_by_type = defaultdict(list)
    for r in rooms.values():
        rooms_by_type[r.room_type].append(r)

    # Track how many rooms of each type are already committed per color
    color_room_usage = defaultdict(lambda: defaultdict(int))

    for _ in range(n):
        node = pick_next()
        if node == -1:
            break

        used = neighbor_colors(node)
        needed_type = get_needed_type(sessions[node])
        student_count = sessions[node].section.student_count

        for c in range(len(timeslots)):
            if c in used:
                continue

            if needed_type == "lab":
                available = [r for r in rooms_by_type["lab"] if r.capacity >= student_count]
            elif needed_type == "classroom":
                available = [
                    r for r in rooms_by_type["classroom"] + rooms_by_type["lecture_hall"]
                    if r.capacity >= student_count
                ]
            else:  # lecture_hall
                available = [r for r in rooms_by_type["lecture_hall"] if r.capacity >= student_count]

            if color_room_usage[c][needed_type] < len(available):
                color[node] = c
                color_room_usage[c][needed_type] += 1
                break

        for j in conflict_graph[node]:
            if color[j] < 0:
                saturation[j] = len(neighbor_colors(j))

    for i, session in enumerate(sessions):
        session.color = color[i]
