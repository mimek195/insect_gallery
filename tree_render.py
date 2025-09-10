from ete3 import Tree, TextFace, add_face_to_node
from ete3.treeview import TreeStyle
import sqlite3


def render_tree(database_name):
    taxonomy = sqlite3.connect(database_name)
    cursor = taxonomy.cursor()

    # Fetch Database
    cursor.execute('''
        SELECT t.name_latin, r.name, st.name_latin
        FROM taxons t
        JOIN ranks r ON t.rank_id = r.id
        LEFT JOIN taxons st ON t.super_taxon_id = st.id
        ''')

    # Database as matrix
    taxonomy = []
    rows = cursor.fetchall()
    for row in rows:
        taxonomy.append((row[0], row[1], row[2]))

    # Build tree
    nodes = {}
    for taxon_name, rank, supertaxon_name in taxonomy:
        if supertaxon_name is None:
            nodes[taxon_name] = Tree(name=taxon_name)
        else:
            supertaxon_node = nodes[supertaxon_name]
            taxon = supertaxon_node.add_child(name=taxon_name)
            nodes[taxon_name] = taxon

    # Tree style
    ts = TreeStyle()
    ts.show_leaf_name = False
    ts.show_scale = False

    # Add faces to nodes
    ts.layout_fn = (lambda node: add_face_to_node(TextFace(node.name), node, column=0, position="branch-right"))
    nodes["Arthropoda"].show(tree_style=ts)
