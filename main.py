import database as db
import gui
db.nuke_database('photos')
db.create_photo_database('photos')
db.load_default('photos')

#db.view_taxonomy('taxonomy.db')
gui.main()
