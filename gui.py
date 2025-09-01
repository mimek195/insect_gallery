import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtGui import QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insect Gallery")
        self.resize(1000, 600)
        self.center()
        self.setWindowIcon(QIcon("icon.png"))



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

