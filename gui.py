import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit,
                             QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QCheckBox, QStackedWidget, QSizePolicy)
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import Qt
import database as db
import phylogenetic_tree_gen as tree

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Set Window Size
        self.setWindowTitle("Insect Gallery")
        self.resize(1000, 600)
        self.setWindowIcon(QIcon("icon.png"))

        self.database_name = None
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # Pages
        self.page0 = QWidget()
        self.page1 = QWidget()

        self.main_menu()

        # Pages
        self.stacked_widget.addWidget(self.page0)
        self.stacked_widget.addWidget(self.page1)

    def main_menu(self):

        main_menu_layout = QVBoxLayout()
        main_menu_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Display Title
        main_menu_title = QLabel("Insect Gallery")
        main_menu_title.setFont(QFont("Arial", 40))
        main_menu_title.setStyleSheet("color: black;")
        main_menu_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Display Image
        pixmap = QPixmap("icon.png")
        main_menu_icon = QLabel()
        main_menu_icon.setPixmap(pixmap)
        main_menu_icon.setScaledContents(True)
        main_menu_icon.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_menu_icon.setMaximumSize(200, 200)

        # Display Line Edit
        self.line_edit = QLineEdit()
        self.line_edit.setFont(QFont("Arial", 11))
        self.line_edit.setPlaceholderText("Enter database name")
        self.line_edit.setFixedWidth(250)
        self.line_edit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Display Line Edit Button
        line_edit_button = QPushButton("Load Database")
        line_edit_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        line_edit_button.setFixedWidth(250)

        # Error Message
        self.error_message = QLabel("Database not found")
        self.error_message.setStyleSheet("color: red;")
        self.error_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_message.setVisible(False)

        # Container for Error Message
        error_container = QWidget()
        error_container.setFixedHeight(20)
        error_layout = QVBoxLayout()
        error_layout.setContentsMargins(0, 0, 0, 0)
        error_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_layout.addWidget(self.error_message)
        error_container.setLayout(error_layout)

        # Connect
        self.line_edit.returnPressed.connect(self.view_database)
        line_edit_button.clicked.connect(self.view_database)

        # Add widgets
        main_menu_layout.addSpacing(-200)
        main_menu_layout.addWidget(main_menu_title, alignment=Qt.AlignmentFlag.AlignCenter)
        main_menu_layout.addSpacing(20)
        main_menu_layout.addWidget(main_menu_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        main_menu_layout.addSpacing(20)
        main_menu_layout.addWidget(self.line_edit, alignment=Qt.AlignmentFlag.AlignCenter)
        main_menu_layout.addWidget(line_edit_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_menu_layout.addSpacing(2)
        main_menu_layout.addWidget(error_container, alignment=Qt.AlignmentFlag.AlignCenter)

        self.page0.setLayout(main_menu_layout)
        self.scan_for_databases()

    def load_database(self):
        load_database_layout = QVBoxLayout()
        load_database_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        list_of_databases = self.scan_for_databases()


        self.page1.setLayout(load_database_layout)

    def view_database(self):
        try:
            self.database_path = os.path.join(self.base_dir, 'databases', self.line_edit.text() + '.db')
            self.line_edit.clear()
            if db.check_if_database_exists(self.database_path):
                if self.error_message.isVisible():
                    self.error_message.setVisible(False)
                self.tree_window = tree.generate_phylogenetic_tree(self.database_path)
                self.tree_window.show()
            else:
                self.error_message.setVisible(True)
        except:
            print("error")

    def scan_for_databases(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        databases_dir = os.path.join(base_dir, 'databases')
        databases = [f for f in os.listdir(databases_dir) if f.endswith('.db')]
        return databases

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

