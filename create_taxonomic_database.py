import re
import sqlite3
import os
input_file = "arthropoda_ids.txt"

lines = [line.rstrip("\n") for line in open(input_file)]

parent_id_list = []  # tracks parent IDs per indentation level
filter_output = []

# regex formula that finds and captures the id, taxon rank, and taxon name
taxon_regex = re.compile(r'^(\d+)\s+\[([^\]]+)\]\s+(.+)$')

base_dir = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(base_dir, 'taxonomy.db')
taxonomy = sqlite3.connect(database_path)
cursor = taxonomy.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS taxons (
        taxon_id INTEGER PRIMARY KEY AUTOINCREMENT,
        taxon_rank TEXT NOT NULL,
        taxon_name TEXT NOT NULL,
        parent_id INTEGER
    )
    ''')

for line in lines:
    if not line.strip():
        continue

    # Line's length without the indentations
    stripped = line.lstrip()
    # Detects indentations
    indentation_level = len(line) - len(stripped)

    regex_match = taxon_regex.match(stripped)
    if not regex_match:
        continue

    taxon_id, taxon_rank, taxon_name = regex_match.groups()
    taxon_rank = taxon_rank.strip().lower()
    taxon_name = taxon_name.strip()

    # Skipping unnecessary or rarely used ranks.
    ignored_ranks = ["no rank", "strain", "isolate", "forma specialis"]
    if any(ignored_rank in taxon_rank for ignored_rank in ignored_ranks):
        continue

    # Filters out uncertain species, marked with sp., ssp., etc. Filters out environmental samples.
    if "." in taxon_name or "environmental sample" in taxon_name:
        continue

    # Check whether list has enough levels
    while len(parent_id_list) <= indentation_level:
        parent_id_list.append(None)

    # Determine parent ID. Last taxon_id with lower indentation level.
    parent_id = ""
    for i in range(indentation_level - 1, -1, -1):
        if parent_id_list[i] is not None:
            parent_id = parent_id_list[i]
            break

    # Update parent_id_list
    parent_id_list[indentation_level] = taxon_id

    # Adds current taxon to the output list
    filter_output.append([taxon_id, taxon_rank, taxon_name, parent_id])


    cursor.execute('''
    INSERT INTO taxons (taxon_id, taxon_rank, taxon_name, parent_id) VALUES (?, ?, ?, ?)
    ''', (taxon_id, taxon_rank, taxon_name, parent_id))

taxonomy.commit()
taxonomy.close()



print("Data filtering and reformatting complete")
