import sys
import os
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QFormLayout, QMessageBox, QSplitter, QMenuBar, QMenu,
    QStatusBar, QDialog, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtGui import QFont

from app.database import DatabaseManager
from app.models import Project, Task, ProjectStatus, TaskPriority
from app.logger import ActivityLogger
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter


class ProjectManagementGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.logger = ActivityLogger()
        self.current_project_id = None
        self.setFont(QFont("Inter", 10))
        self.setup_ui()
        self.load_projects()
        self.update_status_bar()
        self.logger.log_activity("Приложение запущено")


    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Система управления IT-проектами")
        self.setGeometry(100, 50, 1400, 900)

        self.create_menu()

        self.create_central_widget()
        self.create_status_bar()

    def create_menu(self):
        """Создание меню"""
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu("Файл")

        refresh_action = QAction("Обновить", self)
        refresh_action.triggered.connect(self.load_projects)
        file_menu.addAction(refresh_action)

        view_logs_action = QAction("Посмотреть логи", self)
        view_logs_action.triggered.connect(self.show_logs)
        file_menu.addAction(view_logs_action)

        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def create_central_widget(self):
        """Создание центрального виджета"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Разделитель для левой и правой панелей
        splitter = QSplitter(Qt.Horizontal)

        # Левая панель - формы ввода
        left_widget = self.create_left_panel()
        splitter.addWidget(left_widget)

        # Правая панель - таблицы
        right_widget = self.create_right_panel()
        splitter.addWidget(right_widget)

        # Установка пропорций
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)

    def create_left_panel(self):
        """Создание левой панели с формами ввода"""
        left_widget = QWidget()
        layout = QVBoxLayout(left_widget)

        # Группа для формы проекта
        project_group = QGroupBox("Управление проектами")
        project_layout = QVBoxLayout(project_group)

        form_layout = QFormLayout()

        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("Введите название проекта")
        form_layout.addRow("Название:", self.project_name)

        self.project_desc = QLineEdit()
        self.project_desc.setPlaceholderText("Описание проекта")
        form_layout.addRow("Описание:", self.project_desc)

        self.project_start = QLineEdit()
        self.project_start.setText(datetime.now().strftime('%Y-%m-%d'))
        form_layout.addRow("Дата начала (ГГГГ-ММ-ДД):", self.project_start)

        self.project_end = QLineEdit()
        self.project_end.setPlaceholderText("ГГГГ-ММ-ДД")
        form_layout.addRow("Дата окончания:", self.project_end)

        self.project_status = QComboBox()
        self.project_status.addItems([status.value for status in ProjectStatus])
        self.project_status.setCurrentText(ProjectStatus.PLANNING.value)
        form_layout.addRow("Статус:", self.project_status)

        self.project_budget = QLineEdit()
        self.project_budget.setPlaceholderText("0.00")
        form_layout.addRow("Бюджет (₽):", self.project_budget)

        self.project_team = QLineEdit()
        self.project_team.setPlaceholderText("0")
        form_layout.addRow("Размер команды:", self.project_team)

        project_layout.addLayout(form_layout)

        # Кнопки управления проектами
        buttons_layout = QHBoxLayout()
        self.add_project_btn = QPushButton("Добавить проект")
        self.add_project_btn.clicked.connect(self.add_project)
        buttons_layout.addWidget(self.add_project_btn)

        self.delete_project_btn = QPushButton("Удалить проект")
        self.delete_project_btn.clicked.connect(self.delete_selected_project)
        self.delete_project_btn.setStyleSheet("font-family: Inter; background-color: #0078d4; color: white;")
        buttons_layout.addWidget(self.delete_project_btn)

        project_layout.addLayout(buttons_layout)
        layout.addWidget(project_group)

        # Группа для формы задачи
        task_group = QGroupBox("Управление задачами")
        task_layout = QVBoxLayout(task_group)

        task_form_layout = QFormLayout()

        self.task_title = QLineEdit()
        self.task_title.setPlaceholderText("Название задачи")
        task_form_layout.addRow("Заголовок:", self.task_title)

        self.task_assignee = QLineEdit()
        self.task_assignee.setPlaceholderText("Имя исполнителя")
        task_form_layout.addRow("Исполнитель:", self.task_assignee)

        self.task_priority = QComboBox()
        self.task_priority.addItems([priority.value for priority in TaskPriority])
        self.task_priority.setCurrentText(TaskPriority.MEDIUM.value)
        task_form_layout.addRow("Приоритет:", self.task_priority)

        self.task_deadline = QLineEdit()
        self.task_deadline.setPlaceholderText("ГГГГ-ММ-ДД")
        default_deadline = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        self.task_deadline.setText(default_deadline)
        task_form_layout.addRow("Дедлайн:", self.task_deadline)

        task_layout.addLayout(task_form_layout)

        # Кнопки управления задачами
        task_buttons_layout = QHBoxLayout()
        self.add_task_btn = QPushButton("Добавить задачу")
        self.add_task_btn.clicked.connect(self.add_task)
        task_buttons_layout.addWidget(self.add_task_btn)

        self.delete_task_btn = QPushButton("Удалить задачу")
        self.delete_task_btn.clicked.connect(self.delete_selected_task)
        self.delete_task_btn.setStyleSheet("font-family: Inter; background-color: #0078d4; color: white;")
        task_buttons_layout.addWidget(self.delete_task_btn)

        task_layout.addLayout(task_buttons_layout)
        layout.addWidget(task_group)

        layout.addStretch()
        return left_widget

    def create_right_panel(self):
        """Создание правой панели с таблицами"""
        right_widget = QWidget()
        layout = QVBoxLayout(right_widget)

        # Таблица проектов
        projects_label = QLabel("Проекты:")
        projects_label.setStyleSheet("font-family: Inter; font-weight: bold; font-size: 14px;")
        layout.addWidget(projects_label)

        self.projects_table = QTableWidget()
        self.setup_projects_table()
        layout.addWidget(self.projects_table)

        # Таблица задач
        tasks_label = QLabel("Задачи выбранного проекта:")
        tasks_label.setStyleSheet("font-family: Inter; font-weight: bold; font-size: 14px;")
        layout.addWidget(tasks_label)

        self.tasks_table = QTableWidget()
        self.setup_tasks_table()
        layout.addWidget(self.tasks_table)

        return right_widget

    def setup_projects_table(self):
        """Настройка таблицы проектов"""
        self.projects_table.setStyleSheet("font-family: Inter;")
        self.projects_table.setColumnCount(8)
        self.projects_table.setHorizontalHeaderLabels([
            'ID', 'Название', 'Описание', 'Статус', 'Начало', 'Окончание', 'Бюджет', 'Команда'
        ])
        self.projects_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.projects_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.projects_table.setSelectionMode(QTableWidget.SingleSelection)
        self.projects_table.itemSelectionChanged.connect(self.on_project_select)

    def setup_tasks_table(self):
        """Настройка таблицы задач"""
        self.projects_table.setStyleSheet("font-family: Inter;")
        self.tasks_table.setColumnCount(6)
        self.tasks_table.setHorizontalHeaderLabels([
            'ID', 'Заголовок', 'Исполнитель', 'Приоритет', 'Дедлайн', 'Статус'
        ])
        self.tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tasks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tasks_table.setSelectionMode(QTableWidget.SingleSelection)

    def create_status_bar(self):
        """Создание статус бара"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово")

    def add_project(self):
        """Добавление нового проекта"""
        try:
            if not self.project_name.text().strip():
                raise Exception("Название проекта обязательно")

            project = Project(
                id=None,
                name=self.project_name.text().strip(),
                description=self.project_desc.text().strip(),
                start_date=datetime.strptime(self.project_start.text(), '%Y-%m-%d'),
                end_date=datetime.strptime(self.project_end.text(),
                                           '%Y-%m-%d') if self.project_end.text().strip() else None,
                status=ProjectStatus(self.project_status.currentText()),
                budget=float(self.project_budget.text() or 0),
                team_size=int(self.project_team.text() or 0)
            )

            project_id = self.db.add_project(project)
            project.id = project_id

            self.logger.log_project_creation(project)
            self.load_projects()
            self.update_status_bar()
            self.clear_project_form()

            QMessageBox.information(self, "Успех", "Проект успешно добавлен!")

        except ValueError as e:
            self.logger.log_error(e)
            QMessageBox.critical(self, "Ошибка", "Некорректные данные. Проверьте введенные значения.")
        except Exception as e:
            self.logger.log_error(e)
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_task(self):
        """Добавление новой задачи"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите проект")
            return

        try:
            if not self.task_title.text().strip():
                raise Exception("Заголовок задачи обязателен")

            task = Task(
                id=None,
                project_id=self.current_project_id,
                title=self.task_title.text().strip(),
                description="",
                assignee=self.task_assignee.text().strip(),
                priority=TaskPriority(self.task_priority.currentText()),
                deadline=datetime.strptime(self.task_deadline.text(), '%Y-%m-%d'),
                status=ProjectStatus.PLANNING
            )

            task_id = self.db.add_task(task)
            task.id = task_id

            self.logger.log_task_creation(task)
            self.load_tasks()
            self.clear_task_form()

            QMessageBox.information(self, "Успех", "Задача успешно добавлена!")

        except Exception as e:
            self.logger.log_error(e)
            QMessageBox.critical(self, "Ошибка", str(e))

    def delete_selected_project(self):
        """Удаление выбранного проекта"""
        selected_items = self.projects_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Выберите проект для удаления")
            return

        row = selected_items[0].row()
        project_id = int(self.projects_table.item(row, 0).text())
        project_name = self.projects_table.item(row, 1).text()

        tasks = self.db.get_tasks_by_project(project_id)
        tasks_count = len(tasks)

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить проект '{project_name}'?\n"
            f"Все связанные задачи ({tasks_count}) также будут удалены!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                success = self.db.del_project(project_id)

                if success:
                    self.logger.log_activity(
                        f"Удален проект: {project_name} (ID: {project_id}) с {tasks_count} задачами"
                    )

                    self.load_projects()
                    self.update_status_bar()
                    self.current_project_id = None
                    self.tasks_table.setRowCount(0)

                    QMessageBox.information(self, "Успех", "Проект и все связанные задачи удалены!")
                else:
                    QMessageBox.warning(self, "Ошибка", "Проект не найден")

            except Exception as e:
                self.logger.log_error(e)
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления проекта: {str(e)}")

    def delete_selected_task(self):
        """Удаление выбранной задачи"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите проект")
            return

        selected_items = self.tasks_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Выберите задачу для удаления")
            return

        row = selected_items[0].row()
        task_id = int(self.tasks_table.item(row, 0).text())
        task_title = self.tasks_table.item(row, 1).text()

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить задачу '{task_title}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                success = self.db.del_task(task_id)

                if success:
                    self.logger.log_activity(f"Удалена задача: {task_title} (ID: {task_id})")
                    self.load_tasks()
                    self.update_status_bar()
                    QMessageBox.information(self, "Успех", "Задача удалена!")
                else:
                    QMessageBox.warning(self, "Ошибка", "Задача не найдена")

            except Exception as e:
                self.logger.log_error(e)
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления задачи: {str(e)}")

    def load_projects(self):
        """Загрузка проектов в таблицу"""
        try:
            self.projects_table.setRowCount(0)
            projects = self.db.get_all_projects()
            self.projects_table.setRowCount(len(projects))

            for row, project in enumerate(projects):
                self.projects_table.setItem(row, 0, QTableWidgetItem(str(project.id)))
                self.projects_table.setItem(row, 1, QTableWidgetItem(project.name))
                self.projects_table.setItem(row, 2, QTableWidgetItem(project.description))
                self.projects_table.setItem(row, 3, QTableWidgetItem(project.status.value))
                self.projects_table.setItem(row, 4, QTableWidgetItem(project.start_date.strftime('%Y-%m-%d')))
                end_date = project.end_date.strftime('%Y-%m-%d') if project.end_date else '-'
                self.projects_table.setItem(row, 5, QTableWidgetItem(end_date))
                self.projects_table.setItem(row, 6, QTableWidgetItem(f"₽{project.budget:,.2f}"))
                self.projects_table.setItem(row, 7, QTableWidgetItem(str(project.team_size)))

        except Exception as e:
            self.logger.log_error(e)
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки проектов: {str(e)}")

    def load_tasks(self):
        """Загрузка задач выбранного проекта"""
        if not self.current_project_id:
            return

        try:
            self.tasks_table.setRowCount(0)
            tasks = self.db.get_tasks_by_project(self.current_project_id)
            self.tasks_table.setRowCount(len(tasks))

            for row, task in enumerate(tasks):
                self.tasks_table.setItem(row, 0, QTableWidgetItem(str(task.id)))
                self.tasks_table.setItem(row, 1, QTableWidgetItem(task.title))
                self.tasks_table.setItem(row, 2, QTableWidgetItem(task.assignee))
                self.tasks_table.setItem(row, 3, QTableWidgetItem(task.priority.value))
                self.tasks_table.setItem(row, 4, QTableWidgetItem(task.deadline.strftime('%Y-%m-%d')))
                self.tasks_table.setItem(row, 5, QTableWidgetItem(task.status.value))

        except Exception as e:
            self.logger.log_error(e)
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки задач: {str(e)}")

    def on_project_select(self):
        """Обработка выбора проекта"""
        selected_items = self.projects_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.current_project_id = int(self.projects_table.item(row, 0).text())
            self.load_tasks()

    def clear_project_form(self):
        """Очистка формы проекта"""
        self.project_name.clear()
        self.project_desc.clear()
        self.project_start.setText(datetime.now().strftime('%Y-%m-%d'))
        self.project_end.clear()
        self.project_budget.clear()
        self.project_team.clear()
        self.project_status.setCurrentText(ProjectStatus.PLANNING.value)

    def clear_task_form(self):
        """Очистка формы задачи"""
        self.task_title.clear()
        self.task_assignee.clear()
        self.task_deadline.clear()
        default_deadline = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        self.task_deadline.setText(default_deadline)
        self.task_priority.setCurrentText(TaskPriority.MEDIUM.value)

    def update_status_bar(self):
        """Обновление статус бара"""
        try:
            projects = self.db.get_all_projects()
            total_tasks = sum(len(self.db.get_tasks_by_project(p.id)) for p in projects)

            message = f"Проектов: {len(projects)} | Задач: {total_tasks}"
            self.status_bar.showMessage(message)
        except Exception as e:
            self.status_bar.showMessage("Ошибка загрузки статистики")

    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        self.logger.log_activity("Приложение закрыто")
        event.accept()

    def show_logs(self):
        """Показать логи из файла с графиком активности"""
        try:
            if os.path.exists("activity.log"):
                with open("activity.log", 'r', encoding='utf-8') as f:
                    logs = f.read()
                log_dialog = QDialog(self)
                log_dialog.setWindowTitle("Логи и статистика приложения")
                log_dialog.setGeometry(150, 150, 1000, 700)
                layout = QVBoxLayout(log_dialog)
                # Создаем разделитель для логов и графика
                splitter = QSplitter(Qt.Vertical)
                figure = Figure(figsize=(8, 3))
                canvas = FigureCanvas(figure)
                # Анализируем активность по дням
                activity_by_day = self.analyze_activity()
                if activity_by_day:
                    ax = figure.add_subplot(111)
                    dates = list(activity_by_day.keys())
                    counts = list(activity_by_day.values())
                    sorted_data = sorted(zip(dates, counts), key=lambda x: x[0])
                    dates = [item[0] for item in sorted_data]
                    counts = [item[1] for item in sorted_data]
                    formatted_dates = [date.strftime('%d.%m') for date in dates]
                    bars = ax.bar(formatted_dates, counts, color='#4CAF50', alpha=0.7)
                    for bar, count in zip(bars, counts):
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                                f'{count}', ha='center', va='bottom', fontsize=8)
                    ax.set_title('Активность по дням', fontsize=12, fontweight='bold')
                    ax.set_ylabel('Событий')
                    ax.grid(True, alpha=0.3)
                    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
                    figure.tight_layout()
                else:
                    ax = figure.add_subplot(111)
                    ax.text(0.5, 0.5, 'Нет данных для графика',
                            ha='center', va='center', transform=ax.transAxes)
                    ax.set_xticks([])
                    ax.set_yticks([])
                splitter.addWidget(canvas)
                # Нижняя часть - логи
                log_text = QTextEdit()
                log_text.setPlainText(logs)
                log_text.setReadOnly(True)
                log_text.setFontFamily("Courier New")
                log_text.setFontPointSize(9)
                splitter.addWidget(log_text)
                splitter.setSizes([300, 400])
                layout.addWidget(splitter)

                close_btn = QPushButton("Закрыть")
                close_btn.clicked.connect(log_dialog.close)
                layout.addWidget(close_btn)
                log_dialog.exec()
            else:
                QMessageBox.information(self, "Логи", "Файл логов не найден")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать логи: {str(e)}")

    def analyze_activity(self):
        """Анализ логов и подсчет активности по дням"""
        activity_by_day = {}
        try:
            if not os.path.exists("activity.log"):
                return activity_by_day
            with open("activity.log", 'r', encoding='utf-8') as f:
                for line in f:
                    if len(line) >= 19:
                        date_str = line[:10]  # Берем первые 10 символов (YYYY-MM-DD)
                        try:
                            date = datetime.strptime(date_str, '%Y-%m-%d').date()
                            activity_by_day[date] = activity_by_day.get(date, 0) + 1
                        except ValueError:
                            continue
            return activity_by_day
        except Exception as e:
            print(f"Ошибка анализа логов: {e}")
            return {}