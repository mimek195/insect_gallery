import sqlite3
import os


def check_if_database_exists(database_name):
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, database_name)
    if os.path.isfile(file_path):
        return True
    else:
        return False


def create_taxonomic_database(database_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(base_dir, 'databases', database_name + '.db')
    taxonomy = sqlite3.connect(database_path)
    cursor = taxonomy.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create ranks table
    cursor.execute("DROP TABLE IF EXISTS ranks;")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ranks (
        id INTEGER NOT NULL,
        name TEXT NOT NULL,
        super_rank_id INTEGER NOT NULL
    )
    ''')

    ranks = [
        (1, "Species", 0),
        (2, "Genus", 1),
        (3, "Tribe", 2),
        (4, "Subfamily", 3),
        (5, "Family", 4),
        (6, "Superfamily", 5),
        (7, "Suborder", 6),
        (8, "Order", 7),
        (9, "Infraclass", 8),
        (10, "Subclass", 9),
        (11, "Class", 10),
        (12, "Phylum", 11)
    ]
    cursor.executemany('''
        INSERT INTO ranks (id, name, super_rank_id) VALUES (?, ?, ?)
        ''', ranks)

    # Create taxons table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS taxons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rank_id INTEGER NOT NULL,
        name_latin TEXT NOT NULL,
        name_english TEXT,
        description TEXT,
        super_taxon_id INTEGER,
        FOREIGN KEY(rank_id) REFERENCES ranks(id) ON DELETE CASCADE
    )
    ''')

    # Create photos table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS photos (
        photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
        supertaxon_id INTEGER NOT NULL,
        photo_location TEXT,
        photo_description TEXT,
        FOREIGN KEY(supertaxon_id) REFERENCES taxons(id) ON DELETE CASCADE
    )
    ''')

    taxonomy.commit()
    taxonomy.close()


def load_database(database_name):
    database = sqlite3.connect(database_name)
    cursor = database.cursor()


def load_default(database_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(base_dir, 'databases', database_name + '.db')
    taxonomy = sqlite3.connect(database_path)
    cursor = taxonomy.cursor()

    taxas = [
        (12, "Arthropoda", "Arthropod", "Insects, crustaceans and such", None),
        (11, "Insecta", "Insects", "Hexapod invertebrates", 1),
        (8, "Hempitera", "True Bugs", "Bug", 2),
        (6, "Heteroptera", "Typical Bugs", "Different wings!", 3),
        (5, "Pyrrhocoridae", "Red Bugs", "They are red", 4),
        (2, "Pyrrhocoris", "Cotton Stainers", "Yup, red", 5),
        (1, "Pyrrhocoris apterus", "Firebug", "Red!", 6),
        (11, "Crustacea", "Crustaceans", "Crab", 1)
    ]

    cursor.executemany('''
    INSERT INTO taxons (rank_id, name_latin, name_english, description, super_taxon_id) VALUES (?, ?, ?, ?, ?)
    ''', taxas)

    taxonomy.commit()
    taxonomy.close()


def view_taxonomy(database_name):
    taxonomy = sqlite3.connect(database_name)
    cursor = taxonomy.cursor()

    cursor.execute('''
    SELECT taxons.id, taxons.name_latin, taxons.description
    FROM taxons
    ''')

    rows = cursor.fetchall()
    for row in rows:
        print(f"Rank ID: {row[0]}, Name: {row[1]}")
        print(f"Description: {row[2]}")
        print("------")

    taxonomy.close()


def input_rank_id(database_name):
    taxonomy = sqlite3.connect(database_name)
    cursor = taxonomy.cursor()

    cursor.execute('''
        SELECT ranks.id, ranks.name
        FROM ranks
        ''')

    rows = cursor.fetchall()
    while True:
        rank_id_list = []
        print(f"{'Rank ID':<10} {'Name':<20}")
        for row in rows:
            rank_id_list.append(row[0])
            print(f"{row[0]:<10} {row[1]:<20}")
        print("------")
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


def input_supertaxon_id(database_name):
    taxonomy = sqlite3.connect(database_name)
    cursor = taxonomy.cursor()

    cursor.execute('''
        SELECT t.id, t.name_latin, r.name
        FROM taxons t
        JOIN ranks r ON t.rank_id = r.id
        ''')
    rows = cursor.fetchall()
    while True:
        supertaxon_id_list = []
        print(f"{'Supertaxon ID':<20} {'Name':<30} {'Rank Name':<20}")
        for row in rows:
            supertaxon_id_list.append(row[0])
            print(f"{row[0]:<20} {row[1]:<30} {row[2]:<20}")
        print("------")
        try:
            supertaxon_id = int(input("Supertaxon ID: "))
            if any(supertaxon == supertaxon_id for supertaxon in supertaxon_id_list):
                break
            else:
                print("------")
                print("Supertaxon not found")
                print("------")
        except:
            print("------")
            print("ID must be an integer")
            print("------")

    taxonomy.close()
    return supertaxon_id


def input_string(query, limit=50):
    while True:
        try:
            input_result = input(query)
            if len(input_result) <= limit:
                return input_result
            else:
                print(f"String must have less than {limit} symbols")
        except:
            print("unknown error")


def add_taxonomy(database_name):
    taxonomy = sqlite3.connect(database_name)
    cursor = taxonomy.cursor()
    new_rank_id = input_rank_id()
    new_supertaxon_id = input_supertaxon_id()
    new_name_latin = input_string("Input latin name: ", 50)
    new_name_english = input_string("Input common name: ", 50)
    new_description = input_string("Input description: ", 1000)

    new_taxon = (new_rank_id, new_name_latin, new_name_english, new_description, new_supertaxon_id)
    cursor.execute('''
    INSERT INTO taxons (rank_id, name_latin, name_english, description, super_taxon_id) VALUES (?, ?, ?, ?, ?)
    ''', new_taxon)
    taxonomy.commit()
    taxonomy.close()


def nuke_database(database_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(base_dir, 'databases', database_name + '.db')
    os.remove(database_path)
