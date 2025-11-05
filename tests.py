import pytest
import sys
import os
from datetime import datetime

# Добавляем путь к корню проекта для импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import DatabaseManager
from app.models import Project, Task, ProjectStatus, TaskPriority


class TestDatabase:
    """Тесты для базы данных с использованием tmp_path"""

    @pytest.fixture
    def db(self, tmp_path):
        """Создание базы данных во временной директории"""
        db_path = tmp_path / "test.db"
        return DatabaseManager(str(db_path))

    def test_database_initialization(self, db):
        """Тест инициализации базы данных"""
        # Проверяем что база создана и таблицы существуют
        projects = db.get_all_projects()
        assert isinstance(projects, list)
        assert len(projects) == 0

    def test_add_project(self, db):
        """Тест добавления проекта"""
        project = Project(
            id=None,
            name="Тестовый проект",
            description="Описание тестового проекта",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            status=ProjectStatus.PLANNING,
            budget=100000.0,
            team_size=5
        )

        project_id = db.add_project(project)

        assert project_id is not None
        assert project_id > 0

        # Проверяем что проект добавлен в БД
        projects = db.get_all_projects()
        assert len(projects) == 1
        assert projects[0].name == "Тестовый проект"
        assert projects[0].status == ProjectStatus.PLANNING

    def test_add_task(self, db):
        """Тест добавления задачи"""
        # Сначала создаем проект
        project = Project(
            id=None,
            name="Проект для задачи",
            description="Проект для тестирования задач",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 6, 30),
            status=ProjectStatus.IN_PROGRESS,
            budget=50000.0,
            team_size=3
        )
        project_id = db.add_project(project)

        # Создаем задачу
        task = Task(
            id=None,
            project_id=project_id,
            title="Тестовая задача",
            description="Описание тестовой задачи",
            assignee="Иван Иванов",
            priority=TaskPriority.HIGH,
            deadline=datetime(2024, 3, 31),
            status=ProjectStatus.IN_PROGRESS
        )

        task_id = db.add_task(task)

        assert task_id is not None
        assert task_id > 0

        # Проверяем что задача добавлена
        tasks = db.get_tasks_by_project(project_id)
        assert len(tasks) == 1
        assert tasks[0].title == "Тестовая задача"
        assert tasks[0].priority == TaskPriority.HIGH

    def test_delete_project(self, db):
        """Тест удаления проекта"""
        project = Project(
            id=None,
            name="Проект для удаления",
            description="Этот проект будет удален",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            status=ProjectStatus.PLANNING,
            budget=10000.0,
            team_size=2
        )
        project_id = db.add_project(project)

        # Удаляем проект
        result = db.del_project(project_id)
        assert result is True

        # Проверяем что проект удален
        projects = db.get_all_projects()
        assert len(projects) == 0

    def test_delete_task(self, db):
        """Тест удаления задачи"""
        # Создаем проект и задачу
        project = Project(
            id=None,
            name="Проект для теста удаления задачи",
            description="Тест удаления задачи",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            status=ProjectStatus.IN_PROGRESS,
            budget=20000.0,
            team_size=4
        )
        project_id = db.add_project(project)

        task = Task(
            id=None,
            project_id=project_id,
            title="Задача для удаления",
            description="Эта задача будет удалена",
            assignee="Петр Петров",
            priority=TaskPriority.MEDIUM,
            deadline=datetime(2024, 2, 28),
            status=ProjectStatus.IN_PROGRESS
        )
        task_id = db.add_task(task)

        # Удаляем задачу
        result = db.del_task(task_id)
        assert result is True

        # Проверяем что задача удалена
        tasks = db.get_tasks_by_project(project_id)
        assert len(tasks) == 0

    def test_get_tasks_by_project(self, db):
        """Тест получения задач по ID проекта"""
        project = Project(
            id=None,
            name="Проект с задачами",
            description="Проект с несколькими задачами",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            status=ProjectStatus.IN_PROGRESS,
            budget=30000.0,
            team_size=3
        )
        project_id = db.add_project(project)

        # Добавляем несколько задач
        task1 = Task(
            id=None,
            project_id=project_id,
            title="Задача 1",
            description="Первая задача",
            assignee="Иван",
            priority=TaskPriority.HIGH,
            deadline=datetime(2024, 2, 1),
            status=ProjectStatus.IN_PROGRESS
        )

        task2 = Task(
            id=None,
            project_id=project_id,
            title="Задача 2",
            description="Вторая задача",
            assignee="Петр",
            priority=TaskPriority.LOW,
            deadline=datetime(2024, 2, 15),
            status=ProjectStatus.PLANNING
        )

        db.add_task(task1)
        db.add_task(task2)

        # Получаем задачи проекта
        tasks = db.get_tasks_by_project(project_id)

        assert len(tasks) == 2
        assert tasks[0].title == "Задача 1"
        assert tasks[1].title == "Задача 2"

    def test_cascade_delete(self, db):
        """Тест каскадного удаления задач при удалении проекта"""
        # Создаем проект
        project = Project(
            id=None,
            name="Проект для каскадного удаления",
            description="Проверка каскадного удаления",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            status=ProjectStatus.IN_PROGRESS,
            budget=40000.0,
            team_size=3
        )
        project_id = db.add_project(project)

        # Добавляем несколько задач
        for i in range(3):
            task = Task(
                id=None,
                project_id=project_id,
                title=f"Задача {i + 1}",
                description=f"Описание задачи {i + 1}",
                assignee=f"Исполнитель {i + 1}",
                priority=TaskPriority.MEDIUM,
                deadline=datetime(2024, 3, 1),
                status=ProjectStatus.IN_PROGRESS
            )
            db.add_task(task)

        # Проверяем что задачи созданы
        tasks_before = db.get_tasks_by_project(project_id)
        assert len(tasks_before) == 3

        # Удаляем проект
        db.del_project(project_id)

        # Проверяем что проект удален
        projects = db.get_all_projects()
        assert len(projects) == 0

        # Проверяем что задачи тоже удалены (каскадное удаление)
        # При попытке получить задачи несуществующего проекта должна вернуться пустой список
        tasks_after = db.get_tasks_by_project(project_id)
        assert len(tasks_after) == 0

    def test_error_handling(self, db):
        """Тест обработки ошибок"""
        # Попытка удалить несуществующий проект
        result = db.del_project(99999)
        assert result is False

        # Попытка удалить несуществующую задачу
        result = db.del_task(99999)
        assert result is False

        # Попытка получить задачи несуществующего проекта
        tasks = db.get_tasks_by_project(99999)
        assert len(tasks) == 0

    def test_integration_workflow(self, db):
        """Интеграционный тест полного workflow"""

        # 1. Создаем проект
        project = Project(
            id=None,
            name="Интеграционный тест",
            description="Проект для тестирования полного workflow",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 6, 30),
            status=ProjectStatus.PLANNING,
            budget=75000.0,
            team_size=4
        )
        project_id = db.add_project(project)

        # 2. Добавляем задачи
        tasks_data = [
            ("Анализ требований", "Анна", TaskPriority.HIGH),
            ("Разработка", "Иван", TaskPriority.MEDIUM),
            ("Тестирование", "Петр", TaskPriority.LOW)
        ]

        for title, assignee, priority in tasks_data:
            task = Task(
                id=None,
                project_id=project_id,
                title=title,
                description=f"Описание для {title}",
                assignee=assignee,
                priority=priority,
                deadline=datetime(2024, 3, 31),
                status=ProjectStatus.PLANNING
            )
            db.add_task(task)

        # 3. Проверяем что все создалось
        projects = db.get_all_projects()
        assert len(projects) == 1
        assert projects[0].name == "Интеграционный тест"

        tasks = db.get_tasks_by_project(project_id)
        assert len(tasks) == 3

        # 4. Удаляем одну задачу
        task_to_delete = tasks[0].id
        db.del_task(task_to_delete)

        tasks_after_delete = db.get_tasks_by_project(project_id)
        assert len(tasks_after_delete) == 2

        # 5. Удаляем проект (задачи удалятся каскадно)
        db.del_project(project_id)

        projects_after_delete = db.get_all_projects()
        assert len(projects_after_delete) == 0


class TestModels:
    """Тесты для моделей данных"""

    def test_project_creation(self):
        """Тест создания объекта проекта"""
        project = Project(
            id=1,
            name="Тестовый проект",
            description="Описание проекта",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            status=ProjectStatus.IN_PROGRESS,
            budget=150000.0,
            team_size=6
        )

        assert project.id == 1
        assert project.name == "Тестовый проект"
        assert project.status == ProjectStatus.IN_PROGRESS
        assert project.budget == 150000.0
        assert project.team_size == 6

    def test_task_creation(self):
        """Тест создания объекта задачи"""
        task = Task(
            id=1,
            project_id=1,
            title="Тестовая задача",
            description="Описание задачи",
            assignee="Сергей Сергеев",
            priority=TaskPriority.CRITICAL,
            deadline=datetime(2024, 3, 15),
            status=ProjectStatus.TESTING
        )

        assert task.id == 1
        assert task.project_id == 1
        assert task.title == "Тестовая задача"
        assert task.assignee == "Сергей Сергеев"
        assert task.priority == TaskPriority.CRITICAL
        assert task.status == ProjectStatus.TESTING

    def test_project_to_dict(self):
        """Тест преобразования проекта в словарь"""
        project = Project(
            id=1,
            name="Проект для dict",
            description="Описание",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            status=ProjectStatus.COMPLETED,
            budget=99999.99,
            team_size=7
        )

        project_dict = project.to_dict()

        assert project_dict['id'] == 1
        assert project_dict['name'] == "Проект для dict"
        assert project_dict['status'] == "Завершён"
        assert project_dict['budget'] == 99999.99

    def test_task_to_dict(self):
        """Тест преобразования задачи в словарь"""
        task = Task(
            id=1,
            project_id=1,
            title="Задача для dict",
            description="Описание задачи",
            assignee="Анна",
            priority=TaskPriority.MEDIUM,
            deadline=datetime(2024, 4, 1),
            status=ProjectStatus.ON_HOLD
        )

        task_dict = task.to_dict()

        assert task_dict['id'] == 1
        assert task_dict['title'] == "Задача для dict"
        assert task_dict['assignee'] == "Анна"
        assert task_dict['priority'] == "Средний"
        assert task_dict['status'] == "Ожидание"


class TestEnums:
    """Тесты для перечислений"""

    def test_project_status_values(self):
        """Тест значений статусов проектов"""
        assert ProjectStatus.PLANNING.value == "Планируется"
        assert ProjectStatus.IN_PROGRESS.value == "В работе"
        assert ProjectStatus.TESTING.value == "Тестирование"
        assert ProjectStatus.COMPLETED.value == "Завершён"
        assert ProjectStatus.ON_HOLD.value == "Ожидание"

    def test_task_priority_values(self):
        """Тест значений приоритетов задач"""
        assert TaskPriority.LOW.value == "Низкий"
        assert TaskPriority.MEDIUM.value == "Средний"
        assert TaskPriority.HIGH.value == "Высокий"
        assert TaskPriority.CRITICAL.value == "Срочный"

    def test_project_status_from_string(self):
        """Тест создания статуса из строки"""
        status = ProjectStatus("Планируется")
        assert status == ProjectStatus.PLANNING

        status = ProjectStatus("В работе")
        assert status == ProjectStatus.IN_PROGRESS

    def test_task_priority_from_string(self):
        """Тест создания приоритета из строки"""
        priority = TaskPriority("Высокий")
        assert priority == TaskPriority.HIGH

        priority = TaskPriority("Срочный")
        assert priority == TaskPriority.CRITICAL





