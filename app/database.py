import sqlite3
from datetime import datetime
from typing import List, Optional
from app.models import Project, Task, ProjectStatus, TaskPriority

class DatabaseManager:
    def __init__(self, db_path: str = "projects.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                cursor = conn.cursor()

                # Таблица проектов
                cursor.execute('''
                            CREATE TABLE IF NOT EXISTS projects (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                description TEXT,
                                start_date TEXT NOT NULL,
                                end_date TEXT,
                                status TEXT NOT NULL,
                                budget REAL NOT NULL,
                                team_size INTEGER NOT NULL,
                                created_at TEXT DEFAULT CURRENT_TIMESTAMP
                            )
                        ''')

                # Таблица задач с каскадным удалением
                cursor.execute('''
                            CREATE TABLE IF NOT EXISTS tasks (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                project_id INTEGER NOT NULL,
                                title TEXT NOT NULL,
                                description TEXT,
                                assignee TEXT NOT NULL,
                                priority TEXT NOT NULL,
                                deadline TEXT NOT NULL,
                                status TEXT NOT NULL,
                                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                            )
                        ''')
                conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"Ошибка инициализации БД: {e}")

    def add_project(self, project: Project) -> int:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                cursor = conn.cursor()
                cursor.execute('''
                            INSERT INTO projects (name, description, start_date, end_date, status, budget, team_size)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                    project.name,
                    project.description,
                    project.start_date.strftime('%Y-%m-%d'),
                    project.end_date.strftime('%Y-%m-%d') if project.end_date else None,
                    project.status.value,
                    project.budget,
                    project.team_size
                ))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Ошибка добавления проекта: {e}")

    def add_task(self, task: Task) -> int:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                cursor = conn.cursor()
                cursor.execute('''
                            INSERT INTO tasks (project_id, title, description, assignee, priority, deadline, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                    task.project_id,
                    task.title,
                    task.description,
                    task.assignee,
                    task.priority.value,
                    task.deadline.strftime('%Y-%m-%d'),
                    task.status.value
                ))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Ошибка добавления задачи: {e}")

    def del_project(self, project_id: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                cursor = conn.cursor()
                cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Ошибка удаления проекта: {e}")

    def del_task(self, task_id: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                cursor = conn.cursor()
                cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Ошибка удаления задачи: {e}")

    def get_all_projects(self) -> List[Project]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
                rows = cursor.fetchall()

                projects = []
                for row in rows:
                    # Преобразуем строку в datetime для end_date (может быть None)
                    end_date = None
                    if row[4]:  # end_date
                        try:
                            end_date = datetime.strptime(row[4], '%Y-%m-%d')
                        except ValueError:
                            end_date = None

                    # Создаём объект Project со статусом из enum
                    project = Project(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        start_date=datetime.strptime(row[3], '%Y-%m-%d'),
                        end_date=end_date,
                        status=ProjectStatus(row[5]),
                        budget=row[6],
                        team_size=row[7]
                    )
                    projects.append(project)
                return projects
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения проектов: {e}")

    def get_tasks_by_project(self, project_id: int) -> List[Task]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM tasks 
                    WHERE project_id = ? 
                    ORDER BY created_at DESC
                ''', (project_id,))
                rows = cursor.fetchall()

                tasks = []
                for row in rows:
                    # Создаём объект Task с enum значениями
                    task = Task(
                        id=row[0],
                        project_id=row[1],
                        title=row[2],
                        description=row[3],
                        assignee=row[4],
                        priority=TaskPriority(row[5]),
                        deadline=datetime.strptime(row[6], '%Y-%m-%d'),
                        status=ProjectStatus(row[7])
                    )
                    tasks.append(task)
                return tasks
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения задач: {e}")