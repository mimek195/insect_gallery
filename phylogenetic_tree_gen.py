import sqlite3
from PyQt6.QtWidgets import (
    QMainWindow, QGraphicsView, QGraphicsScene,
    QGraphicsTextItem, QGraphicsRectItem, QGraphicsLineItem
)
from PyQt6.QtCore import Qt

def build_taxon_tree(cursor, parent_id=None):
    if parent_id is None:
        cursor.execute("""
                       SELECT t.id, t.name_latin, r.name
                       FROM taxons t
                                JOIN ranks r ON t.rank_id = r.id
                       WHERE t.super_taxon_id IS NULL
                       """)
    else:
        cursor.execute("""
                       SELECT t.id, t.name_latin, r.name
                       FROM taxons t
                                JOIN ranks r ON t.rank_id = r.id
                       WHERE t.super_taxon_id = ?
                       """, (parent_id,))

    nodes = []
    for taxon_id, latin_name, rank_name in cursor.fetchall():
        node = {
            "id": taxon_id,
            "name": latin_name,
            "rank": rank_name,
            "children": build_taxon_tree(cursor, taxon_id)
        }
        nodes.append(node)
    return nodes


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

        # start from arthropoda
        self.draw_tree(tree_data, 0, 0, 1000)

    def draw_tree(self, nodes, depth, x_start, x_width):
        if not nodes:
            return []

        positions = []
        step = x_width / (len(nodes) + 1)

        for i, node in enumerate(nodes):
            x = x_start + (i + 1) * step
            y = depth * self.level_height

            # Box
            node_box = QGraphicsRectItem(x, y, self.box_width, self.box_height)
            node_box.setBrush(Qt.GlobalColor.lightGray)
            node_box.setPen(Qt.GlobalColor.black)
            self.scene.addItem(node_box)

            # Text
            label = f"{node['rank']}: {node['name']}"
            text_item = QGraphicsTextItem(label)
            text_item.setDefaultTextColor(Qt.GlobalColor.black)
            text_item.setTextWidth(self.box_width)
            text_item.setPos(x + 5, y + 5)
            self.scene.addItem(text_item)

            # children positions
            child_positions = self.draw_tree(node['children'], depth + 1, x - step / 2, step)

            # the lines!
            for cx, cy in child_positions:
                line = QGraphicsLineItem(
                    x + self.box_width / 2, y + self.box_height,  # bottom of parent
                    cx + self.box_width / 2, cy  # top of child
                )
                self.scene.addItem(line)

            # position
            positions.append((x, y + self.box_height))

        return positions

def generate_phylogenetic_tree(database_path):
    taxonomy = sqlite3.connect(database_path)
    cursor = taxonomy.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    tree_data = build_taxon_tree(cursor)
    taxonomy.close()

    window = PhylogeneticTree(tree_data)
    return window

