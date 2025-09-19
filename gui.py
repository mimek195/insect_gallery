import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit,
                             QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QCheckBox, QStackedWidget, QSizePolicy)
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import Qt
import database as db
import tree_render as tr


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Set Window Size
        self.setWindowTitle("Insect Gallery")
        self.resize(1000, 600)
        self.center()
        self.setWindowIcon(QIcon("icon.png"))

        self.database_name = None

        self.page1 = QWidget()
        self.main_menu_layout = QVBoxLayout()

        self.page2 = QWidget()
        self.load_database_layout = QVBoxLayout()

        self.main_menu()

    def main_menu(self):
        # Main Menu Elements
        self.main_menu_layout.line_edit = QLineEdit(self)
        self.main_menu_layout.line_button = QPushButton("Display Database", self)
        self.main_menu_layout.title = QLabel("Insect Gallery", self)
        self.main_menu_layout.image = QLabel(self)

        self.main_menu_layout.error_message = QLabel("Database not found", self)

        # Display Title
        self.main_menu_layout.title.setFont(QFont("Arial", 40))
        self.main_menu_layout.title.setGeometry(0, 0, 1000, 100)
        self.main_menu_layout.title.setStyleSheet("color: black;")
        self.main_menu_layout.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_menu_layout.title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Display Image
        pixmap = QPixmap("icon.png")
        self.main_menu_layout.image.setPixmap(pixmap)
        self.main_menu_layout.image.setGeometry(0, 0, 150, 150)
        self.main_menu_layout.image.setScaledContents(True)
        self.main_menu_layout.image.setGeometry(
            (self.width() - self.main_menu_layout.image.width()) // 2,
            (self.height() - self.main_menu_layout.image.height()) // 2,
            self.main_menu_layout.image.width(), self.main_menu_layout.image.height())

        # Display Line Edit
        self.main_menu_layout.line_edit.setGeometry(0, 0, 150, 40)
        self.main_menu_layout.line_edit.setGeometry(
            (self.width() - self.main_menu_layout.line_edit.width()) // 2,
            (self.height() - self.main_menu_layout.line_edit.height()) // 2 + self.main_menu_layout.image.height(),
            self.main_menu_layout.line_edit.width(), self.main_menu_layout.line_edit.height())
        self.main_menu_layout.line_edit.setFont(QFont("Arial", 11))
        self.main_menu_layout.line_edit.setPlaceholderText("Enter database name")
        self.main_menu_layout.line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Display Line Button
        self.main_menu_layout.line_button.setGeometry(0, 0, 100, 40)
        self.main_menu_layout.line_button.setGeometry(
            (self.width() - self.main_menu_layout.line_button.width()) // 2,
            (self.height() - self.main_menu_layout.line_button.height()) // 2 + self.main_menu_layout.image.height() + self.main_menu_layout.line_edit.height(),
            self.main_menu_layout.line_button.width(), self.main_menu_layout.line_button.height())
        self.main_menu_layout.line_edit.returnPressed.connect(self.view_database)
        self.main_menu_layout.line_button.clicked.connect(self.view_database)

        # Display Error Message
        self.main_menu_layout.error_message.setVisible(False)
        self.main_menu_layout.error_message.setGeometry(0, 0, 150, 50)
        self.main_menu_layout.error_message.setGeometry(
            (self.width() - self.main_menu_layout.error_message.width()) // 2,
            (self.height() - self.main_menu_layout.line_edit.height()) // 2 + self.main_menu_layout.image.height() - 35,
            self.main_menu_layout.error_message.width(), self.main_menu_layout.error_message.height())
        self.main_menu_layout.error_message.setStyleSheet("color: red;")
        self.main_menu_layout.error_message.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.page1.setLayout(self.main_menu_layout)

    def load_database(self):
        return "test"

    def view_database(self):
        try:
            self.database_name = self.main_menu_layout.line_edit.text() + '.db'
            self.main_menu_layout.line_edit.clear()
            if db.check_if_database_exists(self.database_name):
                if self.main_menu_layout.error_message.isVisible():
                    self.main_menu_layout.error_message.setVisible(False)
                tr.render_tree(self.database_name)
            else:
                self.main_menu_layout.error_message.setVisible(True)
        except:
            print("error")



    def new_database(self):
        return "test"

    def center(self):
        screen = QApplication.primaryScreen().availableGeometry()   # get screen geometry
        window_size = self.frameGeometry()                          # get window size
        window_center = screen.center()                             # get center of screen
        window_size.moveCenter(window_center)                       # move window
        self.setGeometry(window_size)                               # apply new geometry


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

