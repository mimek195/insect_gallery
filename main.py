import database as db
db.nuke_database()

db.create_taxonomic_database()
db.load_default()

db.add_taxonomy()

db.view_taxonomy()

