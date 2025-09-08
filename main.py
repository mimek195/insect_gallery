import database as db
import gui
db.nuke_database()

db.create_taxonomic_database()
db.load_default()

db.add_taxonomy()

db.view_taxonomy()

gui.main()
