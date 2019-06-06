from database import Database_Handler
from datetime import datetime
from utils import format_table
db = Database_Handler('../data/db.db')

test = db.start_cash_session(str(datetime.utcnow()), '1-2' , 300)
#db.end_cash_session(datetime.utcnow() , 600)

rows , headers = db.get_cash_sessions()
format_table(rows , headers)

db.connection.close()