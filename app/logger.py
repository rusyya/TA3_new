import logging
from datetime import datetime
from app.models import Project, Task


class ActivityLogger:
    def __init__(self, log_file: str = "activity.log"):
        self.log_file = log_file
        self.setup_logger()

    def setup_logger(self):
        """Настройка логгера"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def log_project_creation(self, project: Project):
        """Логирование создания проекта"""
        self.logger.info(f"Создан проект: {project.name} (ID: {project.id})")

    def log_task_creation(self, task: Task):
        """Логирование создания задачи"""
        self.logger.info(f"Создана задача: {task.title} для проекта ID: {task.project_id}")

    def log_error(self, error: Exception):
        """Логирование ошибок"""
        self.logger.error(f"Ошибка: {str(error)}")

    def log_activity(self, message: str):
        """Логирование произвольной активности"""
        self.logger.info(message)