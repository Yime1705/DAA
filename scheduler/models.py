from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Course:
    id: str
    name: str
    sessions_per_week: int
    session_type: str  # lecture, lab, tutorial
    duration_slots: int = 1


@dataclass
class Teacher:
    id: str
    name: str
    course_ids: list = field(default_factory=list)
    unavailable_slots: list = field(default_factory=list)


@dataclass
class Room:
    id: str
    name: str
    capacity: int
    room_type: str  # lecture_hall, lab, classroom


@dataclass
class Section:
    id: str
    name: str
    student_count: int
    course_ids: list = field(default_factory=list)


@dataclass
class TimeSlot:
    id: int
    day: str
    time: str
    display: str


@dataclass
class Session:
    """A single schedulable node in the conflict graph."""
    id: int
    course: Course
    teacher: Teacher
    section: Section
    room: Optional[Room] = None
    timeslot: Optional[TimeSlot] = None
    color: int = -1  # assigned timeslot index
