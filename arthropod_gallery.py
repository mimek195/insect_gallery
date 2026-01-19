import sys
import os
from PyQt6.QtWidgets import (QApplication, QLabel, QLineEdit, QWidget, QVBoxLayout, QGridLayout,
                             QPushButton, QStackedWidget, QSizePolicy, QCompleter, QMainWindow,
                             QGraphicsView, QGraphicsScene,QGraphicsLineItem, QGraphicsTextItem,
                             QGraphicsRectItem, QFileDialog)
from PyQt6.QtGui import QIcon, QFont, QPixmap, QFontMetrics
from PyQt6.QtCore import Qt
import sqlite3
import shutil
def check_if_database_exists(database_name):
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, database_name)
    if os.path.isfile(file_path):
        return True
    else:
        return False

def create_photo_database(database_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(base_dir, 'databases', database_name + '.db')
    database_folder_path = os.path.join(base_dir, 'databases')
    os.makedirs(database_folder_path, exist_ok=True)

    taxonomy = sqlite3.connect(database_path)
    cursor = taxonomy.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create photos table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS photos (
        photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
        taxon_id INTEGER NOT NULL,
        filepath TEXT NOT NULL,
        FOREIGN KEY(taxon_id) REFERENCES taxons(taxon_id) ON DELETE CASCADE
    )
    ''')

    taxonomy.commit()
    taxonomy.close()

def upload_image(database_name, taxon_id, button=None):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(base_dir, 'databases', database_name + '.db')
    photo_folder_path = os.path.join(base_dir, 'images', database_name)

    os.makedirs(photo_folder_path, exist_ok=True)
    file_path, _ = QFileDialog.getOpenFileName(
        button,
        "Select Image",
        "",
        "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
    )
    if not file_path:
        return
    photo_name = os.path.basename(file_path)
    photo_path = os.path.join(photo_folder_path, photo_name)
    shutil.copy(file_path, photo_path)

    connection = sqlite3.connect(database_path)
    photo_cursor = connection.cursor()
    photo_cursor.execute(
        "INSERT INTO photos (taxon_id, filepath) VALUES (?, ?)",
        (taxon_id, photo_path)
    )
    connection.commit()
    connection.close()

def get_entries_with_photos(cursor):
    cursor.execute("SELECT DISTINCT taxon_id FROM photos")
    rows = cursor.fetchall()
    entries_with_photos = set()
    for row in rows:
        taxon_id = row[0]
        entries_with_photos.add(taxon_id)
    return entries_with_photos

def get_entry_ancestors(cursor, photo_taxonomy):
    taxonomy_ids = set(photo_taxonomy)
    taxonomy_stack = list(photo_taxonomy)

    while taxonomy_stack:
        taxon_id = taxonomy_stack.pop()
        cursor.execute(
            "SELECT parent_id FROM taxons WHERE taxon_id = ?",
            (taxon_id,)
        )
        row = cursor.fetchone()
        if row[0] not in taxonomy_ids:
            parent_id = row[0]
            if parent_id != '':
                taxonomy_ids.add(parent_id)
                taxonomy_stack.append(parent_id)

    return taxonomy_ids

def build_taxon_tree(taxonomy_cursor, taxonomy_to_render, entries_with_photos):

    if not taxonomy_to_render:
        return []

    placeholder_for_taxonomy = ','.join('?' for _ in taxonomy_to_render)
    taxonomy_cursor.execute(f'''SELECT taxon_id, taxon_name, taxon_rank, parent_id
                                FROM taxons
                                WHERE taxon_id IN ({placeholder_for_taxonomy})
                             ''', tuple(taxonomy_to_render))

    taxonomy_rows = taxonomy_cursor.fetchall()
    nodes_id = {}
    children = {}

    for taxon_id, taxon_name, taxon_rank, parent_id in taxonomy_rows:
            nodes_id[taxon_id] = {
                "id": taxon_id,
                "taxon_name": taxon_name,
                "taxon_rank": taxon_rank,
                "has_photos": taxon_id in entries_with_photos,
                "children": []
            }
            if parent_id in taxonomy_to_render:
                children.setdefault(parent_id, []).append(taxon_id)
    for parent_id, child_ids in children.items():
        for child_id in child_ids:
            nodes_id[parent_id]["children"].append(nodes_id[child_id])

    roots = [
        node for taxon_id, node in nodes_id.items()
        if next((r[3] for r in taxonomy_rows if r[0] == taxon_id), None) not in taxonomy_to_render
    ]
    return roots

def generate_phylogenetic_tree(photo_database_path, taxonomy_database_path):
    taxonomy_connect = sqlite3.connect(taxonomy_database_path)
    photos_connect = sqlite3.connect(photo_database_path)

    taxonomy_cursor = taxonomy_connect.cursor()
    photos_cursor = photos_connect.cursor()

    taxonomy_cursor.execute("PRAGMA foreign_keys = ON;")
    photos_cursor.execute("PRAGMA foreign_keys = ON;")

    entries_with_photos = get_entries_with_photos(photos_cursor)
    taxonomy_to_render = get_entry_ancestors(taxonomy_cursor, entries_with_photos)

    tree_data = build_taxon_tree(taxonomy_cursor, taxonomy_to_render, entries_with_photos)

    taxonomy_cursor.close()
    photos_cursor.close()

    tree_window = PhylogeneticTree(tree_data, photo_database_path) # errors
    return tree_window

class ImageLabel(QLabel):
    def __init__(self, pixmap: QPixmap):
        super().__init__()
        self.original_pixmap = pixmap

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def resizeEvent(self, event):
        if not self.original_pixmap.isNull():
            self.setPixmap(self.original_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation))
        super().resizeEvent(event)

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
            'SELECT filepath FROM photos WHERE taxon_id = ?', (self.taxon_id,)).fetchall()]
        photo_connection.close()

        image_columns = 3
        for index, photo_path in enumerate(self.photo_path_list):
            image_row = index // image_columns
            image_column = index % image_columns

            pixmap = QPixmap(photo_path)
            label = ImageLabel(pixmap)
            self.grid_layout.addWidget(label, image_row, image_column)

class InteractableQGraphicsRectItem(QGraphicsRectItem):
    def __init__(self, taxon_id, taxon_name, photo_database_path, x, y, text_width, text_height):
        super().__init__(x, y, text_width, text_height)
        self.taxon_name = taxon_name
        self.taxon_id = taxon_id
        self.photo_database_path = photo_database_path
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        self.album_window = ImageGridWindow(self.taxon_id, self.taxon_name, self.photo_database_path)
        self.album_window.show()
        super().mousePressEvent(event)

class PhylogeneticTree(QMainWindow):
    def __init__(self, tree_data, photo_database_path):
        super().__init__()
        self.setWindowTitle("Phylogenetic Tree")
        self.resize(1200, 800)

        self.photo_database_path = photo_database_path

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.scale(0.85,0.85)
        self.setCentralWidget(self.view)

        self.phylogenetic_tree_entry_height_spacing = 75
        self.entry_box_width = 100
        self.entry_box_height = 60
        self.phylogenetic_tree_width_spacing = 50

        self.draw_tree(tree_data, 0, self.phylogenetic_tree_width_spacing)

    def draw_tree(self, nodes, depth, x_start=0):
        if not nodes:
            return []

        positions = []
        x = x_start

        for node in nodes:
            child_positions = self.draw_tree(node['children'], depth + 1, x)

            # Calculate width
            if child_positions:
                subtree_left = min(cx for cx, _ in child_positions)
                subtree_right = max(cx for cx, _ in child_positions)
                x_center = (subtree_left + subtree_right) / 2
            else:
                label = f"{node['taxon_rank']}: {node['taxon_name']}"
                font = QFont("Arial", 10)
                metrics = QFontMetrics(font)
                text_width = metrics.horizontalAdvance(label) + 10
                x_center = x + text_width / 2

            y = depth * self.phylogenetic_tree_entry_height_spacing

            # Box
            label = f"{node['taxon_rank']}: {node['taxon_name']}"
            font = QFont("Arial", 10)
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(label) + 20
            text_height = metrics.height() + 10

            if node['has_photos']:
                node_box = InteractableQGraphicsRectItem(
                    node['id'], node['taxon_name'], self.photo_database_path,
                    x_center - text_width / 2, y, text_width, text_height
                )
                node_box.setBrush(Qt.GlobalColor.red)
            else:
                node_box = QGraphicsRectItem(
                    x_center - text_width / 2, y, text_width, text_height
                )
                node_box.setBrush(Qt.GlobalColor.lightGray)
            node_box.setPen(Qt.GlobalColor.black)
            self.scene.addItem(node_box)
            node_box.setZValue(1)

            # Text
            text_item = QGraphicsTextItem(label)
            text_item.setFont(font)
            text_item.setDefaultTextColor(Qt.GlobalColor.black)
            text_item.setPos(x_center - text_width / 2 + 5, y)
            self.scene.addItem(text_item)
            text_item.setZValue(2)

            # the lines!
            for cx, cy in child_positions:
                line = QGraphicsLineItem(
                    x_center, y + text_height,  # bottom of parent
                    cx, cy  # top of child
                )
                line.setZValue(0)
                self.scene.addItem(line)

            if child_positions:
                x = max(cx + text_width / 2 + self.phylogenetic_tree_width_spacing for cx, _ in child_positions)
                self.phylogenetic_tree_width_spacing += 10
            else:
                x += text_width + self.phylogenetic_tree_width_spacing

            positions.append((x_center, y + text_height))

        return positions

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
        self.taxonomic_database_path = os.path.join(self.base_dir, 'taxonomy.db')

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
        main_menu_title.setStyleSheet("color: red;")
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
        if check_if_database_exists(self.photo_database_path):
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
            self.database_load_message.setText("Taxon found")
            self.database_load_message.setStyleSheet("color: green;")
            self.database_load_message.setVisible(True)
            taxon_name = self.add_photo_line_edit.text()
            taxon_id = self.taxon_name_to_id.get(taxon_name)
            upload_image(self.photo_database_name, taxon_id, self.add_photo_line_edit)
        self.add_photo_line_edit.clear()

    def view_database(self):
        self.tree_window = generate_phylogenetic_tree(self.photo_database_path, self.taxonomic_database_path)
        self.tree_window.show()

    def new_database(self):
        if self.database_name_line_edit.text() != "":
            create_photo_database(self.database_name_line_edit.text())
            self.load_database()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

