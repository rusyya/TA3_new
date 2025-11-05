import sys
from PySide6.QtWidgets import QApplication
from app.gui import ProjectManagementGUI


def main():
    app = QApplication(sys.argv)


    # Настройка стиля приложения
    app.setStyle('windows11')

    window = ProjectManagementGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()