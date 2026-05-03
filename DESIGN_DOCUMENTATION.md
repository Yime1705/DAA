# Project Design & Workflow Breakdown

This document provides a comprehensive breakdown of the GIKI Timetable Scheduler's architecture, data model, and scheduling algorithms.

## 1. System Architecture

The project follows a classic Client-Server architecture:

### Backend (Flask)

- **`app.py`**: The entry point. Handles HTTP requests, manages the in-memory data store, and interfaces with the `GIKIScheduler`.
- **`scheduler.py`**: The "brain" of the project. Contains the data classes and the logic for session generation, graph construction, and optimization.

### Frontend (Vanilla JS/HTML/CSS)

- **`index.html`**: A single-page application (SPA) that provides a rich, interactive UI for data management and timetable visualization.
- **Styling**: Modern dark-mode aesthetic with CSS variables and flexbox/grid layouts.

---

## 2. Core Data Model

The system operates on four primary entities:

1. **Course**: Defines the "what" (ID, name, sessions per week, type).
2. **Teacher**: Defines the "who" (ID, name, assigned courses, unavailability).
3. **Room**: Defines the "where" (ID, name, capacity, type).
4. **Section**: Defines the "audience" (ID, name, student count, enrolled courses).

### The "Session" Concept

A **Session** is the atomic unit of scheduling. It combines a Course, a Teacher, and a Section. If a course has 3 sessions per week, the scheduler generates 3 distinct Session objects to be placed in the timetable.

---

## 3. The Scheduling Workflow

The `generate_schedule()` method follows a strict multi-phase pipeline:

### Phase 0: Data Validation & Pre-processing

- **Orphan Check**: Identifies courses that are missing teachers or sections.
- **Session Generation**: Creates `Session` objects for every weekly class required.

### Phase 1: Conflict Graph Construction

- A graph is built where each node is a **Session**.
- An edge (conflict) is added between two sessions if:
  - They share the same **Teacher**.
  - They share the same **Section**.
- *Note: Room conflicts are handled during the assignment phase to maximize flexibility.*

### Phase 2: DSatur (Graph Coloring)

DSatur (Degree of Saturation) is an advanced greedy coloring algorithm:

1. **Saturation Degree**: Number of different colors assigned to neighbors.
2. **Heuristic**: Always color the node with the highest saturation degree first.
3. **Room-Awareness**: Before assigning a "color" (timeslot), DSatur checks if a physical room of the required type and capacity is actually available in that slot.

### Phase 3: Kempe Chain Optimization

To improve the "quality" of the schedule (soft constraints), we use localized Kempe swaps:

1. Pick two colors $(c_1, c_2)$ and a starting node.
2. Find the connected component (chain) of nodes using only those two colors.
3. Swap the colors within that chain.
4. If the new schedule has a lower **Soft Penalty** (fewer gaps for students, better teacher workload), keep the swap.

### Phase 4: Room Assignment

Once timeslots are fixed, the scheduler greedily assigns the best-fitting physical room to each session based on type and capacity.

---

## 4. Key Design Decisions

- **In-Memory Store**: Uses a Python dictionary for simplicity and speed (no database required for demo).
- **Localized vs. Global Swaps**: Swapping localized Kempe chains preserves the integrity of the graph coloring while allowing for neighborhood search in the solution space.
- **Greedy Room Assignment**: By delaying final room assignment until after timeslots are fixed (but respecting counts during coloring), the algorithm finds valid solutions faster than if rooms were part of the initial state space.

---

## 5. Constraint Logic

| Constraint Type | Implementation |
| :--- | :--- |
| **Hard: Teacher Conflict** | Edge in Conflict Graph |
| **Hard: Section Conflict** | Edge in Conflict Graph |
| **Hard: Room Availability** | Capacity Tracking in DSatur |
| **Soft: Student Gaps** | Penalty in Soft Constraint Function |
| **Soft: Teacher Load** | Penalty for >3 consecutive sessions |
