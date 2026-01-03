import sqlite3
import os


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
        description TEXT,
        FOREIGN KEY(taxon_id) REFERENCES taxons(taxon_id) ON DELETE CASCADE
    )
    ''')

    taxonomy.commit()
    taxonomy.close()

def display_image(photo_id):


def load_default(database_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(base_dir, 'databases', database_name + '.db')
    taxonomy = sqlite3.connect(database_path)
    cursor = taxonomy.cursor()

    photos = [
        (36998, "red"),
        (7459, "apis")
    ]

    cursor.executemany('''
    INSERT INTO photos (taxon_id, description) VALUES (?, ?)
    ''', photos)

    taxonomy.commit()
    taxonomy.close()


def nuke_database(database_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(base_dir, 'databases', database_name + '.db')
    os.remove(database_path)
