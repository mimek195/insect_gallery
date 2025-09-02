import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set Window Size
        self.setWindowTitle("Insect Gallery")
        self.resize(1000, 600)
        self.center()
        self.setWindowIcon(QIcon("icon.png"))

        # Layout
        self.initUI()

        # Display Title
        title = QLabel("Insect Gallery", self)
        title.setFont(QFont("Comic Sans MS", 40))
        title.setGeometry(0, 0, 1000, 100)
        title.setStyleSheet("color: pink;")
                            #"background-color: black;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Display Image
        image = QLabel(self)
        image.setGeometry(200, 200, 150, 150)

        pixmap = QPixmap("icon.png")
        image.setPixmap(pixmap)

        image.setScaledContents(True)
        image.setGeometry((self.width() - image.width()) // 2,
                          (self.height() - image.height() + title.height()) // 2,
                          image.width(),
                          image.height())

    def initUI(self):
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

