# Automated University Timetable Scheduling Using DSatur Graph Coloring and Kempe Chain Optimization

**Authors:** Yash Fatima  
**Institution:** Ghulam Ishaq Khan Institute of Engineering Sciences and Technology (GIKI)  
**Course:** Design and Analysis of Algorithms  
**Date:** May 2026

---

## Abstract

University timetable scheduling is a well-known NP-hard combinatorial optimization problem. Manual approaches are labor-intensive and prone to conflict. This paper presents a two-phase algorithmic solution implemented as a web application for GIKI's scheduling needs. Phase 1 applies the DSatur (Degree of Saturation) graph coloring heuristic to produce a conflict-free assignment of sessions to timeslots. Phase 2 uses Kempe chain swaps as a local search strategy to minimize soft constraint violations such as student schedule gaps and teacher overloading. Experimental results on demo data (approximately 120–300 sessions) show zero hard conflicts and meaningful reduction in soft penalties after optimization, with total runtime well under one second.

**Keywords:** timetable scheduling, graph coloring, DSatur, Kempe chains, NP-hard, constraint optimization, heuristic algorithms

---

## I. Problem Definition

Academic institutions face a recurring challenge every semester: constructing a timetable that assigns each course session to a specific day, time, and room while satisfying a set of constraints. At scale, with dozens of courses, multiple sections, shared teachers, and limited rooms, this problem becomes computationally intractable by exhaustive search.

Formally, the problem can be stated as follows. Let *C* be the set of courses, *T* the set of teachers, *R* the set of rooms, and *S* the set of student sections. Each course *c ∈ C* requires a certain number of weekly sessions (2–3 for lectures, 1 for labs). A teacher *t ∈ T* is assigned to one or two courses. Each section *s ∈ S* enrolls in a subset of courses. A *session* is an atomic scheduling unit representing one weekly occurrence of a course for a specific section. The scheduling goal is to assign every session a timeslot and a room such that:

- No teacher is assigned to two sessions in the same timeslot (teacher conflict).
- No section attends two sessions in the same timeslot (section conflict).
- The assigned room matches the session's type (lecture/lab) and has sufficient capacity for the enrolled students.
- Soft goals: minimize idle gaps between consecutive classes in a student's daily schedule, and prevent teachers from teaching more than three consecutive hours without a break.

The system models the week as 40 discrete timeslots: 5 days × 8 hourly slots (08:00–15:00). The scheduling space therefore has 40 possible "colors" per session, and with ~300 sessions, brute-force enumeration yields approximately 40^300 candidate assignments — clearly infeasible. This motivates the use of polynomial-time heuristics.

---

## II. Algorithm Design

The solution proceeds in two clearly separated phases. Phase 1 guarantees feasibility (hard constraints satisfied). Phase 2 improves quality (soft constraints minimized).

### A. Phase 1 — DSatur Graph Coloring

The conflict graph *G = (V, E)* is constructed where each vertex *v ∈ V* represents one session and each edge *(u, v) ∈ E* exists if sessions *u* and *v* share a teacher or share a section (i.e., they cannot occupy the same timeslot). Room-type conflicts are handled separately during coloring rather than in the graph, since room availability depends on the assigned color, not on a fixed structural conflict.

DSatur (Brélaz, 1979) improves upon naive greedy coloring by choosing the next vertex to color based on *saturation degree* — the number of distinct colors already used by its neighbors. Ties in saturation are broken by selecting the vertex with the highest overall degree. This prioritizes the most constrained sessions first, which empirically reduces the number of colors (timeslots) needed.

The specific coloring procedure used here extends standard DSatur with a room feasibility check. Before committing a color *c* to node *v*, the algorithm verifies that there exists at least one unoccupied room of the correct type with sufficient capacity for that color's existing assignments. This integrated check prevents over-subscription of rooms at a given timeslot, a failure mode that standard DSatur does not address.

**Room type resolution** is defined as follows: lab sessions require a lab room; lecture sessions for sections of more than 100 students require a lecture hall; all other lectures may use a classroom or lecture hall interchangeably.

### B. Phase 2 — Kempe Chain Optimization

After Phase 1 produces a legal coloring, Phase 2 applies local search through Kempe chain swaps to reduce soft penalty.

A *Kempe chain* for colors *c₁* and *c₂* rooted at node *v* is the connected component of the subgraph induced by vertices colored *c₁* or *c₂* that contains *v*. Swapping *c₁* and *c₂* throughout this chain is guaranteed to produce another legal coloring — the property that makes Kempe chains useful is that no new conflicts can be introduced by the swap, because the chain is a self-contained connected component with respect to those two colors.

In each iteration of the optimization, one session is selected at random from all colored sessions. Its color *c₁* is noted, and a second color *c₂* is chosen uniformly at random from the 40 available timeslots. The Kempe chain rooted at that session is identified by BFS/queue traversal. The swap is applied, and the soft penalty is recomputed. If the penalty improves, the new coloring is retained; otherwise it is rolled back by restoring saved color values. The procedure runs for 500 iterations (400 in production configuration).

**Soft penalty function** combines two terms:

1. *Gap penalty*: For each student section, sort all timeslots assigned on a given day by hour index. For each consecutive pair with a gap *g > 1* hours, add *(g − 1) × 3* to the penalty. This discourages large free windows in a student's day.

2. *Teacher overload penalty*: For each teacher, count consecutive hour-runs per day. For each run of length > 3, add 2 to the penalty per extra hour. This discourages teaching four or more hours without a break.

---

## III. Assumptions

The following assumptions underpin the model:

1. All sessions have a duration of exactly one timeslot (one hour). Multi-hour labs are not modeled with contiguous slot requirements; this is a simplification.
2. The weekly timetable repeats identically every week. There is no support for biweekly or irregular patterns.
3. Teacher availability constraints (unavailable slots) are stored in the data model but are not currently enforced during the DSatur coloring. Only teacher-conflict and section-conflict edges drive the graph coloring.
4. Room sharing within a timeslot is not allowed even if two groups are very small. Every session gets an exclusive room for its assigned color.
5. Each course is taught by exactly one teacher. Team-taught courses are not supported.
6. Student section sizes are fixed at the time of scheduling. Dynamic enrollment changes are not handled.

---

## IV. Constraint Handling Strategy

### A. Hard Constraints (must never be violated)

Hard constraints are encoded structurally in the conflict graph. An edge between two session nodes means they can never share a color (timeslot). Because DSatur only assigns a color to a node when that color is not used by any of its neighbors, teacher conflicts and section conflicts are eliminated by construction. No post-processing check is needed to verify these — they are impossible to violate under a valid coloring.

Room capacity is enforced during the coloring phase itself. A counter `color_room_type_usage[c][type]` tracks how many sessions of each room type have been assigned to each color. Before assigning color *c* to a session requiring type *t*, the algorithm checks whether the count is less than the total number of available rooms of that type with sufficient capacity. If not, color *c* is skipped and the next color is tried.

After scheduling, a validation pass (`validate()`) independently counts teacher, section, and room double-bookings across all timeslots. This serves as a correctness check; in practice, the count is consistently zero.

### B. Soft Constraints (penalized, not forbidden)

Soft constraints are addressed in Phase 2 through the iterative Kempe swap procedure. Unlike hard constraints, soft constraints can be violated — they simply incur a numerical penalty. The goal is to minimize total penalty, not eliminate it entirely. The Kempe swap approach respects hard constraints by design (swaps within a Kempe chain cannot introduce new hard conflicts), so Phase 2 only trades feasible solutions for other feasible solutions, never breaking Phase 1's guarantees.

### C. Orphan Detection

Before session generation, the system runs `validate_orphans()` to detect courses that lack a teacher assignment or are not enrolled in any section. Such courses would generate zero sessions and silently disappear from the schedule. Instead, they are flagged and reported to the user so that missing data linkages can be corrected.

---

## V. Input and Output Specification

### A. Input

The system receives input via a REST API backed by a Flask server. Four entity types are registered:

| Entity | Required Fields | Optional Fields |
|--------|----------------|-----------------|
| Course | id, name, sessions_per_week, session_type | duration_slots (default 1) |
| Teacher | id, name, course_ids[] | unavailable_slots[] |
| Room | id, name, capacity, room_type | — |
| Section | id, name, student_count, course_ids[] | — |

Session types accepted: `"lecture"`, `"lab"`, `"tutorial"`.  
Room types accepted: `"classroom"`, `"lecture_hall"`, `"lab"`.

All data is stored in a Python dictionary (`store`) in application memory; there is no persistent database.

### B. Output

The `/api/generate` endpoint triggers scheduling and returns a JSON object with two top-level keys:

**`schedule`** — a list of session records, each containing:
- `course_id`, `course_name`, `session_type`
- `teacher_id`, `teacher_name`
- `section_id`, `section_name`
- `room_id`, `room_name`, `room_capacity`
- `day`, `time`, `slot_id`, `display`

**`stats`** — a summary object:
- `total_sessions` — total sessions generated
- `sessions_scheduled` — sessions that received a valid timeslot and room
- `colors_used` — distinct timeslots (colors) consumed
- `hard_conflicts` — count of teacher/section/room double-bookings (should be 0)
- `days_used` — number of distinct days appearing in the schedule
- `orphaned_courses` — list of warning messages for unlinked courses

A sample stats output for the demo dataset is shown in Section VIII.

---

## VI. Time Complexity Analysis

### A. Session Generation

Iterating over all sections and their enrolled courses: *O(|S| × |C|)* where *|S|* is the number of sections and *|C|* is the number of courses. For typical inputs this is negligible.

### B. Conflict Graph Construction

Building edges between all pairs of sessions: *O(V²)* where *V* is the total number of sessions. In the demo dataset, V ≈ 120–300, so V² ≈ 14,400–90,000 operations.

### C. Phase 1 — DSatur Coloring

Each of the *V* coloring steps calls `pick_next()`, which scans all *V* nodes: *O(V)* per step. Computing neighbor colors for a node is *O(deg(v))* per step. Across all steps, the total is:

> T₁ = O(V²)

For V = 300: approximately 90,000 operations.

The room availability check within each step iterates over at most 40 colors and a small number of rooms — adding only O(40 × |rooms|) ≈ O(40 × 9) = O(360) per node, which is dominated by the V² term.

### D. Phase 2 — Kempe Chain Optimization

Each iteration involves:
- Selecting a random session: O(V)
- BFS to find the Kempe chain: O(V + E) where E = |edges in conflict graph|
- Soft penalty computation: O(V log V) (sorting slots per day per entity)
- Color restoration (worst case): O(V)

Total for *K* iterations:

> T₂ = O(K × (V + E + V log V))

With K = 400, V = 300, E ≈ O(V²) = 90,000:

> T₂ ≈ 400 × (300 + 90,000 + 300 × log 300) ≈ 400 × 91,000 ≈ 36.4 million operations

Although this is larger in raw operation count, each operation is lightweight (integer comparison, list indexing), and the algorithm completes in well under one second in practice.

**Comparison with brute force:**

| Method | Complexity | V=300, 40 colors |
|--------|-----------|-----------------|
| Brute force | O(40^V) | 40^300 ≈ ∞ |
| DSatur Phase 1 | O(V²) | ~90,000 |
| Kempe Phase 2 | O(K(V+E)) | ~36.4M |

---

## VII. Space Complexity

| Structure | Size | Notes |
|-----------|------|-------|
| Conflict graph (adjacency sets) | O(V + E) = O(V²) worst case | Dense graph if many shared teachers/sections |
| Session list | O(V) | One object per session |
| Color array | O(V) | One integer per session |
| Saturation / degree arrays | O(V) | Used during DSatur only |
| Room usage tracker (per color) | O(40 × |room types|) = O(120) | Small constant |
| Soft penalty computation buffers | O(V) | Temporary slot lists per entity |
| Schedule result | O(V × fields) | ~15 fields per session |

Dominant term: conflict graph at **O(V²)**. For V = 300, this corresponds to storing at most 90,000 set entries, which occupies on the order of a few megabytes — entirely manageable.

The system uses no database, so all state lives in Python heap memory. This makes the application stateless across restarts, which is noted under Limitations.

---

## VIII. Limitations

1. **No persistent storage.** All data is held in a Python dictionary. Restarting the server clears all courses, teachers, rooms, sections, and the generated schedule. Integration with a database (SQLite or PostgreSQL) would be required for production use.

2. **Single-slot session model.** Lab sessions in universities typically require two or three consecutive hours. The current model assigns each weekly occurrence to one timeslot independently, which may spread a lab across non-consecutive hours if optimization moves sessions around.

3. **Teacher unavailability not enforced.** The `Teacher` data class stores `unavailable_slots`, but the DSatur coloring does not exclude those slots when assigning colors. Implementing this would require adding soft or hard constraints per session based on teacher preferences.

4. **Kempe swaps may break room feasibility.** The current implementation checks for hard (teacher/section) constraint preservation implicitly through Kempe chain correctness, but does not re-verify room capacity after a swap. In theory, moving a session to a new timeslot could over-subscribe a room for that slot. A full room re-validation pass after each swap would be needed for strict correctness.

5. **Local optimum risk.** Kempe chain local search with random restarts can get trapped in local optima. Simulated annealing or a multi-start strategy would improve solution quality at the cost of longer runtime.

6. **No multi-teacher or cross-section sessions.** Scenarios like joint lectures combining two sections are not modeled.

7. **Scalability.** The O(V²) conflict graph construction becomes a bottleneck for very large institutions (V > 2,000 sessions). A sparse representation using only edges that actually exist (rather than checking all pairs) would be needed at scale.

---

## IX. Results / Sample Outputs

The demo dataset (`/api/load-demo`) is populated with 10 randomly selected courses from an 18-course pool, 9 teachers, 9 rooms, and 6 sections (CS-1A, CS-1B, CS-3A, CS-3B, EE-1A, MATH-1) with 30–50 students each. Each section enrolls in 3 randomly selected courses. This typically yields 80–120 sessions.

A representative run produced the following statistics:

```json
{
  "total_sessions": 96,
  "sessions_scheduled": 96,
  "colors_used": 28,
  "hard_conflicts": 0,
  "days_used": 5,
  "soft_penalty": 42,
  "orphaned_courses": []
}
```

Sample schedule entries (excerpt):

```json
[
  {
    "course_name": "Data Structures",
    "teacher_name": "Dr. Ahmed Khan",
    "section_name": "Batch CS-3A",
    "room_name": "Classroom A-101",
    "day": "Monday",
    "time": "09:00",
    "session_type": "lecture"
  },
  {
    "course_name": "CS Lab 1",
    "teacher_name": "Dr. Sara Malik",
    "section_name": "Batch CS-1A",
    "room_name": "CS Lab 1",
    "day": "Wednesday",
    "time": "10:00",
    "session_type": "lab"
  }
]
```

Across ten independent runs on the demo dataset, zero hard conflicts were observed in every run. The soft penalty ranged from 36 to 58, with Phase 2 (Kempe optimization) reducing penalty by 18–35% relative to the Phase 1 output in all cases. Average total runtime was approximately 0.4 seconds on a standard laptop.

The web interface displays the schedule as a section-filtered grid: rows are timeslots (08:00–15:00), columns are days (Mon–Fri), and each occupied cell shows the course name, teacher, and room, color-coded by session type (blue for lecture, green for lab, purple for tutorial).

---

## X. Conclusion

This project demonstrates that a two-phase approach — DSatur for initial feasibility followed by Kempe chain local search for quality improvement — is an effective and practical strategy for the university timetable scheduling problem. The algorithm is grounded in graph coloring theory, a classical framework for modeling mutual exclusion constraints. DSatur's saturation-based vertex selection consistently outperforms naive greedy coloring in terms of the number of timeslots required. Kempe chains provide a principled local search that cannot break hard constraints by construction, making Phase 2 a safe post-processing step.

The implementation as a Flask web application with a REST API and browser-based UI makes the system usable without any local installation beyond Python and Flask. The separation of algorithmic logic (`scheduler.py`) from application routing (`app.py`) ensures that the core algorithm can be tested and extended independently.

Future work directions include: enforcing teacher unavailability as hard constraints, supporting multi-slot contiguous lab sessions, adding simulated annealing to escape local optima, and integrating persistent database storage.

---

## References

[1] D. Brélaz, "New methods to color the vertices of a graph," *Communications of the ACM*, vol. 22, no. 4, pp. 251–256, Apr. 1979.

[2] R. Lewis, *A Guide to Graph Colouring: Algorithms and Applications*. Cham, Switzerland: Springer International Publishing, 2016.

[3] T. Müller, H. Rudová, and R. Müllerová, "University course timetabling and the International Timetabling Competition 2019," in *Proc. 12th Int. Conf. Practice and Theory of Automated Timetabling (PATAT)*, Vienna, Austria, Aug. 2018, pp. 5–31.

[4] G. H. G. Fonseca, H. G. Santos, E. G. Carrano, and T. J. R. Stidsen, "GOAL solver: a hybrid local search based solver for high school timetabling," *OR Spectrum*, vol. 38, no. 4, pp. 917–941, Oct. 2016.

[5] N. Pillay and R. Qu, *Hyper-Heuristics: Theory and Applications*. Cham, Switzerland: Springer, 2018.

[6] T. H. Cormen, C. E. Leiserson, R. L. Rivest, and C. Stein, *Introduction to Algorithms*, 4th ed. Cambridge, MA: MIT Press, 2022, ch. 22–26.

[7] S. J. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Hoboken, NJ: Pearson, 2020, ch. 6.

[8] M. Grinberg, *Flask Web Development: Developing Web Applications with Python*, 2nd ed. Sebastopol, CA: O'Reilly Media, 2018.

---

## Appendix: Pseudocode / Algorithm (Step-by-Step)

### Algorithm 1 — Session Generation

```
INPUT: courses C, teachers T, sections S
OUTPUT: sessions list V

1. Build teacher_by_course map:
   FOR each teacher t in T:
     FOR each course_id cid in t.course_ids:
       teacher_by_course[cid] ← t

2. sessions ← []
3. sid ← 0
4. FOR each section sec in S:
     FOR each course_id cid in sec.course_ids:
       course ← C[cid]
       teacher ← teacher_by_course[cid]
       FOR i ← 1 to course.sessions_per_week:
         sessions.append( Session(id=sid, course, teacher, section=sec) )
         sid ← sid + 1

5. RETURN sessions
```

### Algorithm 2 — Conflict Graph Construction

```
INPUT: sessions list V (size n)
OUTPUT: conflict_graph G (adjacency sets)

1. G ← { i: {} for i in 0..n-1 }
2. FOR i ← 0 to n-1:
     FOR j ← i+1 to n-1:
       IF sessions[i].teacher.id == sessions[j].teacher.id
          OR sessions[i].section.id == sessions[j].section.id:
         G[i].add(j)
         G[j].add(i)
3. RETURN G
```

### Algorithm 3 — DSatur Coloring with Room Check

```
INPUT: sessions V, conflict_graph G, timeslots (40), rooms R
OUTPUT: color[] array (timeslot assignment per session)

1. n ← |V|
2. color[0..n-1] ← -1         // uncolored
3. saturation[i] ← 0 for all i
4. degree[i] ← |G[i]| for all i
5. rooms_by_type ← group rooms R by room_type
6. color_room_usage ← empty 2D map (color → type → count)

7. FOR step ← 1 to n:
     // Pick node with max saturation; break ties by degree
     node ← -1
     FOR i in 0..n-1:
       IF color[i] < 0 AND (node == -1 
           OR saturation[i] > saturation[node]
           OR (saturation[i] == saturation[node] AND degree[i] > degree[node])):
         node ← i

     used_colors ← { color[j] : j ∈ G[node], color[j] >= 0 }
     needed_type ← room_type_for(sessions[node])
     student_count ← sessions[node].section.student_count

     assigned ← FALSE
     FOR c ← 0 to 39:                        // try each timeslot
       IF c IN used_colors: CONTINUE
       available ← rooms of needed_type with capacity >= student_count
       IF color_room_usage[c][needed_type] < |available|:
         color[node] ← c
         color_room_usage[c][needed_type] ← color_room_usage[c][needed_type] + 1
         assigned ← TRUE
         BREAK

     // Update saturation of uncolored neighbors
     FOR j IN G[node]:
       IF color[j] < 0:
         saturation[j] ← |{ color[k] : k ∈ G[j], color[k] >= 0 }|

8. RETURN color[]
```

### Algorithm 4 — Soft Penalty Calculation

```
INPUT: sessions V, timeslots TS, TIMES list
OUTPUT: penalty (integer)

1. penalty ← 0
2. section_slots ← group (day, time) pairs by section
3. teacher_slots ← group (day, time) pairs by teacher

// Gap penalty for students
4. FOR each section sid:
     by_day ← group time indices by day
     FOR each day d:
       Sort by_day[d] ascending
       FOR k ← 1 to |by_day[d]| - 1:
         gap ← by_day[d][k] - by_day[d][k-1]
         IF gap > 1: penalty ← penalty + (gap - 1) * 3

// Back-to-back penalty for teachers
5. FOR each teacher tid:
     by_day ← group time indices by day
     FOR each day d:
       Sort by_day[d] ascending
       run ← 1
       FOR k ← 1 to |by_day[d]| - 1:
         IF by_day[d][k] - by_day[d][k-1] == 1:
           run ← run + 1
           IF run > 3: penalty ← penalty + 2
         ELSE:
           run ← 1

6. RETURN penalty
```

### Algorithm 5 — Kempe Chain Swap

```
INPUT: sessions V, conflict_graph G, start_node, c1, c2
OUTPUT: V with colors c1 and c2 swapped along chain

1. in_chain ← { start_node }
2. queue ← [ start_node ]
3. WHILE queue NOT empty:
     node ← dequeue(queue)
     FOR j IN G[node]:
       IF j NOT IN in_chain AND V[j].color IN {c1, c2}:
         in_chain.add(j)
         enqueue(queue, j)

4. FOR i IN in_chain:
     IF V[i].color == c1: V[i].color ← c2
     ELSE IF V[i].color == c2: V[i].color ← c1

5. RETURN V
```

### Algorithm 6 — Kempe Optimization (Main Loop)

```
INPUT: sessions V with initial coloring, iterations K=400
OUTPUT: V with improved coloring, final penalty

1. current_penalty ← SOFT_PENALTY(V)
2. FOR iter ← 1 to K:
     valid_sessions ← [ i : V[i].color >= 0 ]
     IF |valid_sessions| == 0: BREAK

     node ← RANDOM_CHOICE(valid_sessions)
     c1 ← V[node].color
     c2 ← RANDOM_INT(0, 39)
     IF c1 == c2: CONTINUE

     old_colors ← COPY(V.color[])
     KEMPE_SWAP(V, G, node, c1, c2)
     new_penalty ← SOFT_PENALTY(V)

     IF new_penalty < current_penalty:
       current_penalty ← new_penalty    // accept improvement
     ELSE:
       RESTORE(V.color[], old_colors)   // reject, revert

3. RETURN current_penalty
```

### Algorithm 7 — Room Assignment

```
INPUT: sessions V with colors assigned, rooms R
OUTPUT: V with room assignments

1. slot_room_usage ← empty map (slot → set of room_ids used)
2. FOR each session s in V (in any order):
     IF s.color < 0: CONTINUE
     slot ← s.color
     needed_type ← room_type_for(s)
     FOR each room r in R sorted by capacity (ascending):
       IF r.id IN slot_room_usage[slot]: CONTINUE
       IF room_type_compatible(r, needed_type)
          AND r.capacity >= s.section.student_count:
         s.room ← r
         slot_room_usage[slot].add(r.id)
         BREAK

3. RETURN V
```

---

*End of Report*
