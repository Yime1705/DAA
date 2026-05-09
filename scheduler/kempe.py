import random
from collections import defaultdict
from .utils import TIMES


def soft_penalty(sessions, timeslots):
    """
    Calculate total soft constraint penalty:
    - Gap penalty:     3 pts per idle hour in a section's daily schedule
    - Overload penalty: 2 pts per hour a teacher exceeds 3 consecutive sessions
    """
    penalty = 0
    section_slots = defaultdict(list)
    teacher_slots = defaultdict(list)

    for s in sessions:
        if s.color < 0:
            continue
        ts = timeslots[s.color]
        section_slots[s.section.id].append((ts.day, ts.time))
        teacher_slots[s.teacher.id].append((ts.day, ts.time))

    for slots in section_slots.values():
        by_day = defaultdict(list)
        for day, time in slots:
            by_day[day].append(TIMES.index(time))
        for times in by_day.values():
            times.sort()
            for k in range(1, len(times)):
                gap = times[k] - times[k - 1]
                if gap > 1:
                    penalty += (gap - 1) * 3

    for slots in teacher_slots.values():
        by_day = defaultdict(list)
        for day, time in slots:
            by_day[day].append(TIMES.index(time))
        for times in by_day.values():
            times.sort()
            run = 1
            for k in range(1, len(times)):
                if times[k] - times[k - 1] == 1:
                    run += 1
                    if run > 3:
                        penalty += 2
                else:
                    run = 1

    return penalty


def kempe_swap(sessions, conflict_graph, start_node, c1, c2):
    """Swap colors c1 and c2 across the Kempe chain rooted at start_node."""
    in_chain = {start_node}
    queue = [start_node]

    while queue:
        node = queue.pop(0)
        for j in conflict_graph[node]:
            if j not in in_chain and sessions[j].color in (c1, c2):
                in_chain.add(j)
                queue.append(j)

    for i in in_chain:
        s = sessions[i]
        if s.color == c1:
            s.color = c2
        elif s.color == c2:
            s.color = c1


def run_kempe_optimize(sessions, conflict_graph, timeslots, iterations=500):
    """
    Phase 2: Kempe chain local search.
    Randomly swaps color pairs along Kempe chains; keeps the swap only if
    soft penalty improves. Hard constraints are safe by construction.
    Complexity: O(iterations * (V + E))
    """
    num_colors = len(timeslots)
    current_penalty = soft_penalty(sessions, timeslots)

    for _ in range(iterations):
        valid = [i for i, s in enumerate(sessions) if s.color >= 0]
        if not valid:
            break

        node_idx = random.choice(valid)
        c1 = sessions[node_idx].color
        c2 = random.randint(0, num_colors - 1)
        if c1 == c2:
            continue

        old_colors = [s.color for s in sessions]
        kempe_swap(sessions, conflict_graph, node_idx, c1, c2)
        new_penalty = soft_penalty(sessions, timeslots)

        if new_penalty < current_penalty:
            current_penalty = new_penalty
        else:
            for i, s in enumerate(sessions):
                s.color = old_colors[i]

    return current_penalty
