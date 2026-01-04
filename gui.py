import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit,
                             QWidget, QVBoxLayout, QGridLayout,
                             QPushButton, QStackedWidget, QSizePolicy,
                             QCompleter)
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import Qt
import sqlite3
import database as db
import phylogenetic_tree_gen as tree

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Set Window Size
        self.setWindowTitle("Arthropod Gallery")
        self.resize(800, 800)
        self.setWindowIcon(QIcon("icon.png"))

        # Databases
        self.photo_database_name = None

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.taxonomic_database_path = os.path.join(self.base_dir, 'full_taxonomy.db')

        taxonomy = sqlite3.connect(self.taxonomic_database_path)
        taxonomy_cursor = taxonomy.cursor()
        taxonomy_cursor.execute("""SELECT taxon_id, taxon_name FROM taxons""")
        taxonomy_rows = taxonomy_cursor.fetchall()
        self.taxon_name_to_id = {name: taxon_id for taxon_id, name in taxonomy_rows}
        self.taxonomy_names_list = list(self.taxon_name_to_id.keys())

        taxonomy.close()

        # Widgets
        self.database_name_line_edit = QLineEdit()
        self.add_photo_line_edit = QLineEdit()
        self.database_load_message = QLabel("")
        self.view_database_button = QPushButton("View Database")
        self.add_photo_line_button = QPushButton("Add Photo")

        # Pages
        self.page0 = QWidget()
        self.page1 = QWidget()
        self.stacked_widget.addWidget(self.page0)
        self.stacked_widget.addWidget(self.page1)

        self.main_menu()

    def main_menu(self):

        main_menu_layout = QVBoxLayout()
        main_menu_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Display Title
        main_menu_title = QLabel("Arthropod Gallery")
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
        self.database_name_line_edit.setFont(QFont("Arial", 11))
        self.database_name_line_edit.setPlaceholderText("Enter database name")
        self.database_name_line_edit.setFixedWidth(250)
        self.database_name_line_edit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Load Database Line Edit Button
        load_database_line_edit_button = QPushButton("Load Database")
        load_database_line_edit_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        load_database_line_edit_button.setFixedWidth(250)

        # New Database Line Edit Button
        new_database_line_edit_button = QPushButton("New Database")
        new_database_line_edit_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        new_database_line_edit_button.setFixedWidth(250)

        # Upload Photo Line Edit
        add_photo_edit_button_completer = QCompleter(self.taxonomy_names_list)
        add_photo_edit_button_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        add_photo_edit_button_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        add_photo_edit_button_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.add_photo_line_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.add_photo_line_button.setFixedWidth(250)
        self.add_photo_line_button.setEnabled(False)


        self.add_photo_line_edit.setEnabled(False)
        self.add_photo_line_edit.setCompleter(add_photo_edit_button_completer)
        self.add_photo_line_edit.setFont(QFont("Arial", 11))
        self.add_photo_line_edit.setPlaceholderText("Enter Name")
        self.add_photo_line_edit.setFixedWidth(250)
        self.add_photo_line_edit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        new_database_line_edit_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        new_database_line_edit_button.setFixedWidth(250)

        # Database Load Status Message
        self.database_load_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.database_load_message.setVisible(False)

        # Container for Error Message
        database_load_container = QWidget()
        database_load_container.setFixedHeight(20)
        database_load_layout = QVBoxLayout()
        database_load_layout.setContentsMargins(0, 0, 0, 0)
        database_load_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        database_load_layout.addWidget(self.database_load_message)
        database_load_container.setLayout(database_load_layout)

        # View Database Button
        self.view_database_button.setEnabled(False)
        self.view_database_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.view_database_button.setFixedWidth(250)

        # Connect
        self.database_name_line_edit.returnPressed.connect(self.load_database)
        self.add_photo_line_edit.returnPressed.connect(self.upload_image_gui)
        self.view_database_button.clicked.connect(self.view_database)
        load_database_line_edit_button.clicked.connect(self.load_database)
        new_database_line_edit_button.clicked.connect(self.new_database)
        self.add_photo_line_button.clicked.connect(self.upload_image_gui)

        # Add widgets
        main_menu_layout.addSpacing(-200)
        main_menu_layout.addWidget(main_menu_title, alignment=Qt.AlignmentFlag.AlignCenter)
        main_menu_layout.addSpacing(20)
        main_menu_layout.addWidget(main_menu_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        main_menu_layout.addSpacing(20)
        main_menu_layout.addWidget(database_load_container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_menu_layout.addSpacing(2)
        main_menu_layout.addWidget(self.database_name_line_edit, alignment=Qt.AlignmentFlag.AlignCenter)
        main_menu_layout.addSpacing(2)
        main_menu_layout.addWidget(load_database_line_edit_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_menu_layout.addSpacing(2)
        main_menu_layout.addWidget(new_database_line_edit_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_menu_layout.addSpacing(2)
        main_menu_layout.addWidget(self.view_database_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_menu_layout.addSpacing(20)
        main_menu_layout.addWidget(self.add_photo_line_edit, alignment=Qt.AlignmentFlag.AlignCenter)
        main_menu_layout.addSpacing(2)
        main_menu_layout.addWidget(self.add_photo_line_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.page0.setLayout(main_menu_layout)

    def load_database(self):
        self.photo_database_path = os.path.join(self.base_dir, 'databases', self.database_name_line_edit.text() + '.db')
        if db.check_if_database_exists(self.photo_database_path):
            self.database_load_message.setText("Database loaded")
            self.database_load_message.setStyleSheet("color: green;")
            self.database_load_message.setVisible(True)
            self.view_database_button.setEnabled(True)
            self.add_photo_line_edit.setEnabled(True)
            self.add_photo_line_button.setEnabled(True)
            self.photo_database_name = self.database_name_line_edit.text()
        else:
            self.database_load_message.setText("Database not found")
            self.database_load_message.setStyleSheet("color: red;")
            self.database_load_message.setVisible(True)
        self.database_name_line_edit.clear()

    def upload_image_gui(self):
        if self.add_photo_line_edit.text() not in self.taxonomy_names_list:
            self.database_load_message.setText("Taxon not found")
            self.database_load_message.setStyleSheet("color: red;")
            self.database_load_message.setVisible(True)
        else:
            taxon_name = self.add_photo_line_edit.text()
            taxon_id = self.taxon_name_to_id.get(taxon_name)
            db.upload_image(self.photo_database_name, taxon_id, self.add_photo_line_edit)
        self.add_photo_line_edit.clear()

    def view_database(self):
        self.tree_window = tree.generate_phylogenetic_tree(self.photo_database_path, self.taxonomic_database_path)
        self.tree_window.show()

    def new_database(self):
        if self.database_name_line_edit.text() != "":
            db.create_photo_database(self.database_name_line_edit.text())
            self.load_database()

class ImageGridWindow(QWidget):
    def __init__(self, taxon_id, taxon_name, photo_database_path):
        super().__init__()
        self.setWindowTitle(f"{taxon_name}")
        self.resize(800, 600)

        self.photo_database_path = photo_database_path
        self.taxon_name = taxon_name
        self.taxon_id = taxon_id

        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)

        photo_connection = sqlite3.connect(photo_database_path)
        photo_cursor = photo_connection.cursor()

        self.photo_path_list = [row[0] for row in photo_cursor.execute(
            'SELECT filepath FROM photos WHERE taxon_id = ?', (self.taxon_id,)
        ).fetchall()]
        photo_connection.close()

        image_columns = 3
        for index, photo_path in enumerate(self.photo_path_list):
            image_row = index // image_columns
            image_column = index % image_columns

            pixmap = QPixmap(photo_path)
            label = QLabel()
            label.setPixmap(pixmap)
            self.grid_layout.addWidget(label, image_row, image_column)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

