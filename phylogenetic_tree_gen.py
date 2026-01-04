import sqlite3

from PyQt6.QtGui import QFontMetrics, QFont
from PyQt6.QtWidgets import (
    QMainWindow, QGraphicsView, QGraphicsScene,QGraphicsLineItem,
    QGraphicsTextItem, QGraphicsRectItem
)
from PyQt6.QtCore import Qt
import gui


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

class InteractableQGraphicsRectItem(QGraphicsRectItem):
    def __init__(self, taxon_id, taxon_name, photo_database_path, x, y, text_width, text_height):
        super().__init__(x, y, text_width, text_height)
        self.taxon_name = taxon_name
        self.taxon_id = taxon_id
        self.photo_database_path = photo_database_path
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        self.album_window = gui.ImageGridWindow(self.taxon_id, self.taxon_name, self.photo_database_path)
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
            text_item.setPos(x_center - text_width / 2 + 5, y + 5)
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