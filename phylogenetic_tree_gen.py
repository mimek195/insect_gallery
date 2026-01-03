import sqlite3

from PyQt6.QtGui import QFontMetrics, QFont
from PyQt6.QtWidgets import (
    QMainWindow, QGraphicsView, QGraphicsScene,
    QGraphicsTextItem, QGraphicsRectItem, QGraphicsLineItem
)
from PyQt6.QtCore import Qt
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


def build_taxon_tree(taxonomy_cursor, taxonomy_to_render):

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


class PhylogeneticTree(QMainWindow):
    def __init__(self, tree_data):
        super().__init__()
        self.setWindowTitle("Phylogenetic Tree")
        self.resize(1200, 800)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        self.level_height = 100
        self.box_width = 100
        self.box_height = 60
        self.h_spacing = 40

        self.draw_tree(tree_data, 0, 0, 1000)

    def draw_tree(self, nodes, depth, x_start, x_width):
        if not nodes:
            return []

        positions = []
        step = x_width / max(len(nodes), 1)

        for i, node in enumerate(nodes):

            child_positions = self.draw_tree(node['children'], depth + 1, x_start + i*step, step)

            x = x_start + (i + 1) * step
            y = depth * self.level_height

            # Text
            label = f"{node['taxon_rank']}: {node['taxon_name']}"
            text_item = QGraphicsTextItem(label)
            text_item.setDefaultTextColor(Qt.GlobalColor.black)
            #text_item.setTextWidth(self.box_width)
            text_item.setPos(x + 5, y + 5)
            font = QFont("Arial", 10)
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(label) + 10
            text_height = metrics.height() + 10

            # Box
            node_box = QGraphicsRectItem(x, y, text_width+15, text_height)
            node_box.setBrush(Qt.GlobalColor.lightGray)
            node_box.setPen(Qt.GlobalColor.black)

            # the lines!
            for cx, cy in child_positions:
                line = QGraphicsLineItem(
                    x + self.box_width / 2, y + text_height + 2,  # bottom of parent
                    cx + self.box_width / 2, cy - text_height - 2 # top of child
                )
                line.setZValue(0)
                self.scene.addItem(line)
            self.scene.addItem(node_box)
            self.scene.addItem(text_item)
            node_box.setZValue(1)
            text_item.setZValue(2)
            # position
            positions.append((x, y + self.box_height))

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

    tree_data = build_taxon_tree(taxonomy_cursor, taxonomy_to_render)

    taxonomy_cursor.close()
    photos_cursor.close()

    window = PhylogeneticTree(tree_data) # errors
    return window

