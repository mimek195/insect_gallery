import sqlite3
import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox
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


