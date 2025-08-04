import sqlite3
import os


def create_taxonomic_database():
    taxonomy = sqlite3.connect('taxonomy.db')
    cursor = taxonomy.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ranks (
        id INTEGER NOT NULL,
        name TEXT NOT NULL,
        super_rank_id INTEGER NOT NULL
    )
    ''')

    ranks = [
        (1, "Phylum", 0),
        (2, "Class", 1),
        (3, "Subclass", 2),
        (4, "Infraclass", 3),
        (5, "Order", 4),
        (6, "Suborder", 5),
        (7, "Superfamily", 6),
        (8, "Family", 7),
        (9, "Subfamily", 8),
        (10, "Tribe", 9),
        (11, "Genus", 10),
        (12, "Species", 11)
    ]
    cursor.executemany('''
        INSERT INTO ranks (id, name, super_rank_id) VALUES (?, ?, ?)
        ''', ranks)

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS taxonomic_rank (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rank_id INTEGER NOT NULL,
        name_latin TEXT NOT NULL,
        name_english TEXT,
        description TEXT,
        super_taxon_id INTEGER NOT NULL,
        FOREIGN KEY(rank_id) REFERENCES ranks(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS photos (
        photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
        species_id INTEGER NOT NULL,
        photo_location TEXT NOT NULL,
        photo_description TEXT,
        description TEXT,
        FOREIGN KEY(species_id) REFERENCES taxonomic_rank(id) ON DELETE CASCADE
    )
    ''')

    taxonomy.commit()
    taxonomy.close()


def load_default():
    taxonomy = sqlite3.connect('taxonomy.db')
    cursor = taxonomy.cursor()

    taxas = [
        (1, "Arthropoda", "Arthropod", "Insects, crustaceans and such", 0),
        (2, "Insecta", "Insects", "Hexapod invertebrates", 1),
        (5, "Hempitera", "True Bugs", "Bug", 2),
        (6, "Heteroptera", "Typical Bugs", "Different wings!", 3),
        (8, "Pyrrhocoridae", "Red Bugs", "They are red", 4),
        (11, "Pyrrhocoris", "Cotton Stainers", "Yup, red", 5),
        (12, "Pyrrhocoris apterus", "Firebug", "Red!", 6)
    ]

    cursor.executemany('''
    INSERT INTO taxonomic_rank (rank_id, name_latin, name_english, description, super_taxon_id) VALUES (?, ?, ?, ?, ?)
    ''', taxas)

    taxonomy.commit()
    taxonomy.close()


def view_taxonomy():
    taxonomy = sqlite3.connect('taxonomy.db')
    cursor = taxonomy.cursor()

    cursor.execute('''
    SELECT taxonomic_rank.id, taxonomic_rank.name_latin, taxonomic_rank.description
    FROM taxonomic_rank
    ''')

    rows = cursor.fetchall()
    for row in rows:
        print(f"Rank ID: {row[0]}, Name: {row[1]}")
        print(f"Description: {row[2]}")
        print("------")

    taxonomy.close()


def input_rank_id():
    taxonomy = sqlite3.connect('taxonomy.db')
    cursor = taxonomy.cursor()

    cursor.execute('''
        SELECT ranks.id, ranks.name
        FROM ranks
        ''')

    rows = cursor.fetchall()
    while True:
        rank_id_list = []
        for row in rows:
            rank_id_list.append(row[0])
            print(f"Rank ID: {row[0]}, Name: {row[1]}")
        print(rank_id_list)
        try:
            rank_id = int(input("Rank ID: "))
            if any(rank == rank_id for rank in rank_id_list):
                break
            else:
                print("------")
                print("Rank not found")
                print("------")
        except:
            print("------")
            print("ID must be an integer")
            print("------")

    taxonomy.close()
    return rank_id

def input_supertaxon_id():

def add_taxonomy():
    taxonomy = sqlite3.connect('taxonomy.db')
    cursor = taxonomy.cursor()
    while True:
        new_rank_id = input_rank_id()
        new_name_latin = input("Latin name")
        new_name_english = input("English name")
        new_description = input("Description")
        new_supertaxon_id = input("Supertaxon ID")
        break
    new_taxon = (new_rank_id, new_name_latin, new_name_english, new_description, new_supertaxon_id)
    cursor.execute('''
    INSERT INTO taxonomic_rank (rank_id, name_latin, name_english, description, super_taxon_id) VALUES (?, ?, ?, ?, ?)
    ''', new_taxon)
    taxonomy.commit()
    taxonomy.close()


def nuke_database():
    os.remove('taxonomy.db')
