from datetime import datetime
from dataclasses import dataclass
from enum import  Enum
from typing import Optional

class ProjectStatus(Enum):
    """Перечисление статусов проекта"""
    PLANNING = "Планируется"
    IN_PROGRESS = "В работе"
    TESTING = "Тестирование"
    COMPLETED = "Завершён"
    ON_HOLD = "Ожидание"

class TaskPriority(Enum):
    """Перечисление приоритетов задачи"""
    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"
    CRITICAL = "Срочный"


@dataclass
class Project:
    """Класс проекта"""
    id: Optional[int]
    name: str
    description: str
    start_date: datetime
    end_date: Optional[datetime]
    status: ProjectStatus
    budget: float
    team_size: int

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'status': self.status.value,
            'budget': self.budget,
            'team_size': self.team_size
        }


@dataclass
class Task:
    """Класс задачи"""
    id: Optional[int]
    project_id: int
    title: str
    description: str
    assignee: str
    priority: TaskPriority
    deadline: datetime
    status: ProjectStatus

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'assignee': self.assignee,
            'priority': self.priority.value,
            'deadline': self.deadline.strftime('%Y-%m-%d'),
            'status': self.status.value
        }