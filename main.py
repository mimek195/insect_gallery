import database as db
import gui
#db.add_taxonomy('taxonomy.db')

#db.view_taxonomy('taxonomy.db')
print(db.check_if_database_exists("taxonomy"))
gui.main()
