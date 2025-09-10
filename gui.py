import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit,
                             QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QCheckBox)
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import Qt
import database as db
import tree_render as tr


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set Window Size
        self.setWindowTitle("Insect Gallery")
        self.resize(1000, 600)
        self.center()
        self.setWindowIcon(QIcon("icon.png"))

        # Elements
        self.line_edit = QLineEdit(self)
        self.line_button = QPushButton("Display Database", self)
        self.title = QLabel("Insect Gallery", self)
        self.image = QLabel(self)
        self.database_name = None
        self.error_message = QLabel("Database not found", self)

        # Layout
        self.initUI()

    def initUI(self):
        # Display Title
        self.title.setFont(QFont("Arial", 40))
        self.title.setGeometry(0, 0, 1000, 100)
        self.title.setStyleSheet("color: black;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Display Image
        pixmap = QPixmap("icon.png")
        self.image.setPixmap(pixmap)

        self.image.setGeometry(0, 0, 150, 150)
        self.image.setScaledContents(True)
        self.image.setGeometry(
            (self.width() - self.image.width()) // 2,
            (self.height() - self.image.height()) // 2,
            self.image.width(), self.image.height())

        # Display Line Edit
        self.line_edit.setGeometry(0, 0, 150, 40)
        self.line_edit.setGeometry(
            (self.width() - self.line_edit.width()) // 2,
            (self.height() - self.line_edit.height()) // 2 + self.image.height(),
            self.line_edit.width(), self.line_edit.height())
        self.line_edit.setFont(QFont("Arial", 11))
        self.line_edit.setPlaceholderText("Enter database name")

        # Display Line Button
        self.line_button.setGeometry(0, 0, 100, 40)
        self.line_button.setGeometry(
            (self.width() - self.line_button.width()) // 2,
            (self.height() - self.line_button.height()) // 2 + self.image.height() + self.line_edit.height(),
            self.line_button.width(), self.line_button.height())

        self.line_button.clicked.connect(self.view_database_button)

        # Display Error Message
        self.error_message.setVisible(False)
        self.error_message.setGeometry(0, 0, 150, 50)
        self.error_message.setGeometry(
            (self.width() - self.error_message.width()) // 2,
            (self.height() - self.line_edit.height()) // 2 + self.image.height() - 35,
            self.error_message.width(), self.error_message.height())
        self.error_message.setStyleSheet("color: red;")
        self.error_message.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def view_database_button(self):
        try:
            self.database_name = self.line_edit.text() + '.db'
            self.line_edit.clear()
            if db.check_if_database_exists(self.database_name):
                tr.render_tree(self.database_name)
                if self.error_message.isVisible():
                    self.error_message.setVisible(False)
            else:
                self.error_message.setVisible(True)
        except:
            print("error")



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

