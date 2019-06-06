import sqlite3
from pathlib import Path
import dateutil.parser
class Database_Handler:
    
    def __init__ (self , db_path):
        if Path(db_path).is_file():
            self.connection = sqlite3.connect(db_path)
            
        else:
            self.connection = sqlite3.connect(db_path)
            c = self.connection.cursor()
            c.execute(' CREATE TABLE CASHGAMES ( Starttime date NOT NULL , Endtime date , SB int , BB int , Buyin int , Cashout int, email TEXT NOT NULL  ) ')
            c.execute(' CREATE TABLE TOURNAMENTS ( Date date NOT NULL PRIMARY KEY , Name text, Buyin int , bullets int  ,Cashout int , email TEXT NOT NULL  ) ')
            c.execute(' CREATE TABLE USERINFO (email NOT NULL PRIMARY KEY , initial_roll int )')

    def start_cash_session(self , date , SB,  BB , buyin , email ):
        sql = '''INSERT into CASHGAMES(Starttime , Endtime , SB , BB, Buyin , Cashout , email) VALUES(?,?,?,?,?,?,?)'''
        c = self.connection.cursor()
        try:
            c.execute(sql , (date , None , SB , BB , buyin , None , email))
            self.connection.commit()
        except:
            raise 
        return c.lastrowid
    def enter_tournament(self , date , name , buyin , email ):
        sql = ''' INSERT into TOURNAMENTS(Date , Name , Buyin , Cashout) VALUES(?,?,?,?,?)'''
        c = self.connection.cursor()
        try:
            c.execute(sql , (date , name , buyin , None, email))
            self.connection.commit()
        except:
            raise
        return

    def cashout_tournament(self , date , cashout , email):
        sql = 'UPDATE TOURNAMENT SET Cashout=? WHERE Date =? AND email = ?'
        c = self.connection.cursor()
        try:
            c.execute(sql , (cashout , date , email))
            self.connection.commit()
        except:
            raise

    def end_cash_session(self , starttime, endtime , cashout , email ):
        sql = 'UPDATE CASHGAMES SET Endtime=? , Cashout=? Where Starttime=? AND email=?'
        c = self.connection.cursor()
        try:
            c.execute(sql , (endtime , cashout , starttime , email))
            self.connection.commit()
        except:
            raise
        return

    def get_cash_sessions(self , email):
        c = self.connection.cursor()
        c.execute('SELECT Starttime , EndTime , SB , BB , Buyin , Cashout from CASHGAMES WHERE email=?' , (email,))
    
        rows = c.fetchall()
        
        return rows , ['Start Time' , 'End Time' , 'SB'  ,'BB' , 'Buyin' , 'Cash Out']

    def get_cash_session(self , date , email):

        c = self.connection.cursor()
        c.execute('SELECT Starttime , EndTime , SB , BB , Buyin , Cashout from CASHGAMES where email=? and Starttime=?' , (email , date))
        
        d = {}
        for item , key in zip(c.fetchone() , ['Start Time' , 'End Time' , 'SB'  ,'BB' , 'Buyin' , 'Cash Out']):
            d[key] = item
        
        return d


    def get_tournaments_sessions(self):
        c = self.connection.cursor()
        c.execute('SELECT * from TOURNAMENTS')
        rows = c.fetchall()
        headers = [d[0] for d in c.description]
        return rows, headers

    def remove_cash_entry(self , date , email):
        c = self.connection.cursor()
        sql = "DELETE FROM CASHGAMES WHERE Starttime=? AND email=?"
        c.execute( sql , (date,email))
        self.connection.commit()
        return

    def has_account(self , email):
        c = self.connection.cursor()
        sql = "SELECT email FROM USERINFO WHERE email=?"
        c.execute(sql , (email,))
        d = c.fetchall()
        print(len(d))
        return len(d) > 0
    
    def create_account(self , email , inital_Roll):
        c = self.connection.cursor()
        sql = "INSERT into USERINFO VALUES(?,?)"
        c.execute(sql , (email, inital_Roll))
        self.connection.commit()
        return

    def update_SB(self , SB , date , email):

        c = self.connection.cursor()
        sql = "UPDATE CASHGAMES SET SB=? WHERE Starttime=? and email=?"
        try:
            c.execute(sql  , (SB  , date , email))
            self.connection.commit()
        except:
            raise
        return

    def update_BB(self , BB , date , email):

        c = self.connection.cursor()
        sql = "UPDATE CASHGAMES SET BB=? WHERE Starttime=? and email=?"
        try:
            c.execute(sql  , (BB  , date , email))
            self.connection.commit()
        except:
            raise
        return


    def update_Buyin(self , buyin , date , email):

        c = self.connection.cursor()
        sql = "UPDATE CASHGAMES SET Buyin=? WHERE Starttime=? and email=?"
        try:
            c.execute(sql  , (buyin  , date , email))
            self.connection.commit()
        except:
            raise
        return