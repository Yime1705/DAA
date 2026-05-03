# GIKI Timetable Scheduler

A powerful class scheduling system using Graph Coloring (DSatur) and localized Kempe Chain Optimization.

## Features

- **DSatur Algorithm**: Ensures all hard constraints (teacher/section/room availability) are met with zero conflicts.
- **Kempe Chain Optimization**: Iteratively reduces soft penalties such as gaps in student schedules and teacher workloads.
- **Dynamic Room Allocation**: Automatically assigns rooms based on session type (lecture, lab, lecture hall) and capacity.
- **Real-time Validation**: Detects and reports orphaned courses (missing teachers or sections) and hard conflicts.
- **Modern UI**: Dark-themed, responsive dashboard for managing courses, teachers, rooms, and sections.

## Technology Stack

- **Backend**: Python, Flask, Flask-CORS
- **Frontend**: HTML5, Vanilla JavaScript, Syne/DM Mono Fonts
- **Core Logic**: Custom implementation of DSatur and Kempe Chain algorithms.

## Getting Started

### Prerequisites

- Python 3.8+

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Yime1705/DAA.git
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5001`.

### Usage

1. Click **Load Demo Data** to populate the system with sample GIKI data.
2. Go to the **Generate** tab and click **Generate Timetable**.
3. View the results in the **Timetable** tab, filtered by student section.

## License

MIT License
