import database as db
import gui
db.nuke_database('taxonomy')
db.create_taxonomic_database('taxonomy')
db.load_default('taxonomy')

#db.view_taxonomy('taxonomy.db')
gui.main()
