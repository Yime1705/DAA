# GIKI Timetable Scheduler

An automated university timetable scheduling system built for GIKI. Uses a two-phase algorithm — **DSatur graph coloring** for hard constraint satisfaction and **Kempe chain local search** for soft constraint optimization.

---

## How It Works

### Phase 1 — DSatur Graph Coloring `O(V²)`

Each class session is a node in a conflict graph. An edge is drawn between any two sessions that share a teacher or a student section (they cannot occupy the same timeslot). DSatur colors the graph by always picking the most-constrained uncolored node first (highest saturation degree), guaranteeing zero teacher and section conflicts.

Room capacity is also checked during coloring — a timeslot is only assigned if a compatible, unoccupied room exists for it.

### Phase 2 — Kempe Chain Optimization `O(K·(V+E))`

After a valid schedule exists, 400 iterations of Kempe chain swaps reduce soft penalties:

- **Gap penalty** — 3 pts per idle hour in a student section's daily schedule
- **Overload penalty** — 2 pts per hour a teacher teaches more than 3 consecutive sessions

A Kempe swap exchanges two colors (timeslots) along a connected subgraph. By construction it cannot introduce hard conflicts, so feasibility is always preserved.

---

## Project Structure

```
DAA/
├── app.py              # Flask REST API and in-memory data store
├── scheduler.py        # Core algorithm: DSatur + Kempe chains
├── templates/
│   └── index.html      # Single-page frontend (HTML + vanilla JS)
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.8+

### Installation

```bash
git clone https://github.com/Yime1705/DAA.git
cd DAA
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5001` in your browser.

### Quick Demo

1. Click **Load Demo Data** in the top bar — this populates 10 courses, 9 teachers, 9 rooms, and 6 sections.
2. Go to the **GN** (Generate) tab and click **Generate Timetable**.
3. Switch to the **TT** (Timetable) tab and filter by section to view the result.

---

## Manual Data Entry

Use the sidebar tabs to add your own data before generating:

| Tab | What to add |
|-----|------------|
| CR — Courses | Course ID, name, type (lecture/lab/tutorial), sessions per week |
| TC — Teachers | Teacher ID, name, assigned courses |
| RM — Rooms | Room ID, name, type (classroom/lecture hall/lab), capacity |
| SC — Sections | Section ID, name, student count, enrolled courses |

---

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/courses` | List all courses |
| `POST` | `/api/courses` | Add a course |
| `DELETE` | `/api/courses/<id>` | Remove a course |
| `GET` | `/api/teachers` | List all teachers |
| `POST` | `/api/teachers` | Add a teacher |
| `DELETE` | `/api/teachers/<id>` | Remove a teacher |
| `GET` | `/api/rooms` | List all rooms |
| `POST` | `/api/rooms` | Add a room |
| `DELETE` | `/api/rooms/<id>` | Remove a room |
| `GET` | `/api/sections` | List all sections |
| `POST` | `/api/sections` | Add a section |
| `DELETE` | `/api/sections/<id>` | Remove a section |
| `POST` | `/api/generate` | Run the scheduling algorithm |
| `GET` | `/api/schedule` | Retrieve the last generated schedule |
| `GET` | `/api/summary` | Get entity counts and schedule status |
| `POST` | `/api/load-demo` | Populate with GIKI demo data |
| `POST` | `/api/reset` | Clear all data |

### Example — Add a course

```bash
curl -X POST http://localhost:5001/api/courses \
  -H "Content-Type: application/json" \
  -d '{"id":"CS301","name":"Data Structures","sessions_per_week":3,"session_type":"lecture"}'
```

### Example — Generate schedule

```bash
curl -X POST http://localhost:5001/api/generate
```

Response includes a `schedule` array and a `stats` object:

```json
{
  "stats": {
    "total_sessions": 96,
    "sessions_scheduled": 96,
    "colors_used": 28,
    "hard_conflicts": 0,
    "days_used": 5,
    "soft_penalty": 42,
    "orphaned_courses": []
  }
}
```

---

## Constraints

| Constraint | Type | Enforcement |
|-----------|------|-------------|
| No teacher double-booking | Hard | Conflict graph edge |
| No section double-booking | Hard | Conflict graph edge |
| Room type matches session type | Hard | DSatur room check |
| Room capacity >= section size | Hard | DSatur room check |
| Minimize student schedule gaps | Soft | Kempe optimization |
| Limit teacher consecutive hours | Soft | Kempe optimization |

---

## Complexity

| Phase | Complexity | Typical ops (V=300) |
|-------|-----------|---------------------|
| Conflict graph build | O(V²) | ~90,000 |
| DSatur coloring | O(V²) | ~90,000 |
| Kempe optimization | O(K·(V+E)) | ~36M |
| Brute force (baseline) | O(40^V) | infeasible |

---

## Tech Stack

- **Backend** — Python 3.8+, Flask 3.0, Flask-CORS
- **Frontend** — HTML5, Vanilla JavaScript (no framework), CSS custom properties
- **Fonts** — Syne (display), DM Mono (monospace)
- **Storage** — In-memory Python dict (no database; resets on server restart)

---

## License

MIT
