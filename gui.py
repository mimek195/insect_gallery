import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel,
                             QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QCheckBox)
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import Qt
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
        self.button = QPushButton("Render Tree", self)
        self.title = QLabel("Insect Gallery", self)
        self.image = QLabel(self)

        # Layout
        self.initUI()

    def initUI(self):
        '''
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label_1 = QLabel("Arthropoda", self)
        label_2 = QLabel("Insecta", self)
        label_3 = QLabel("Crustacea", self)
        label_4 = QLabel("Heteroptera", self)
        label_5 = QLabel("Pyrrhocoridae", self)

        grid_layout_manager = QGridLayout()
        grid_layout_manager.addWidget(label_1, 0, 2)
        grid_layout_manager.addWidget(label_2, 1, 1)
        grid_layout_manager.addWidget(label_3, 1, 3)
        grid_layout_manager.addWidget(label_4, 2, 1)
        grid_layout_manager.addWidget(label_5, 3, 1)

        central_widget.setLayout(grid_layout_manager)
        '''

        # Display Title
        self.title.setFont(QFont("Times New Roman", 40))
        self.title.setGeometry(0, 0, 1000, 100)
        self.title.setStyleSheet("color: black;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Display Image
        pixmap = QPixmap("icon.png")
        self.image.setPixmap(pixmap)

        self.image.setGeometry(0, 0, 150, 150)
        self.image.setScaledContents(True)
        self.image.setGeometry((self.width() - self.image.width()) // 2,
                          (self.height() - self.image.height()) // 2,
                          self.image.width(),
                          self.image.height())

        # Display Button
        self.button.setGeometry(100, 100, 150, 50)
        self.button.setGeometry((self.width() - self.button.width()) // 2,
                           (self.height() - self.button.height()) // 2 + self.image.height(),
                           self.button.width(),
                           self.button.height())
        self.button.setFont(QFont("Times New Roman", 11))
        self.button.clicked.connect(self.on_click)

    def on_click(self):
        self.button.setText("Tree Rendered")
        self.button.setDisabled(True)
        tr.render_tree()

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

