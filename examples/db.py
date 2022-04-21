from notanorm import SqliteDb 

# https://github.com/AtakamaLLC/notanorm
# https://www.sqlitetutorial.net
# https://www.sqlitetutorial.net/sqlite-create-table/
# https://www.sqlite.org
# https://stackoverflow.com/questions/1309989/parameter-substitution-for-a-sqlite-in-clause
# https://www.sqlitetutorial.net/sqlite-autoincrement/
# https://pymotw.com/2/sqlite3/
# https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html

def main():
 
    #fname = 'tests/profiles.db'
    fname = ":memory:"
    db = SqliteDb(fname) 

    table_station = """
        CREATE TABLE station (
	    id INTEGER PRIMARY KEY,
	    date_time TEXT NOT NULL UNIQUE,
	    julian_day REAL NOT NULL UNIQUE,
	    latitude REAL NOT NULL ,
	    longitude REAL NOT NULL,
        max_depth REAL,
        bottom_depth REAL
        );"""

    # the id is actually the rowid AUTOINCREMENT column.
    table_profile = """
        CREATE TABLE profile (
        id INTEGER PRIMARY KEY,
        station_id INTEGER,
        PRES REAL NOT NULL,
        FOREIGN KEY (station_id) 
            REFERENCES station (id) 
        ); """

    print('Create table station')
    #db.query("DROP DATABASE IF EXISTS '{}'".format(fname))
    db.query(table_station)

    print('Create table profile')
    db.query(table_profile)
    for pm in ("TEMP", "PSAL"):
        print('\tUpdate table profile with new column {}'.format(pm))
        addColumn = "ALTER TABLE profile ADD COLUMN {} REAL NOT NULL".format(pm)
        db.query(addColumn)

    print('Insert data in table station ')
    db.insert("station", id = 1, date_time = "2022-04-06 12:00:00.000",
        julian_day = 10.5, latitude = -10.2, longitude = 23.6)
    db.insert("station", id = 2, date_time = "2022-04-07 17:00:00.000",
        julian_day = 11.5, latitude = -10.2, longitude = 23.6, max_depth = 2001, 
        bottom_depth = 5032)
  
    column = "id"
    result_set = db.select('station', {column: 1})
    for result in result_set:   
        print(result)
    result_set = db.select('station', {column: 2})
    for result in result_set:   
        print(result)

    print('Insert data in profile table')
    db.insert("profile",  station_id = 1, PRES = 1, TEMP = 20, PSAL = 35)
    db.insert("profile",  station_id = 1, PRES = 2, TEMP = 21, PSAL = 35)
    db.insert("profile",  station_id = 1, PRES = 3, TEMP = 22, PSAL = 35)
    db.insert("profile",  station_id = 1, PRES = 3, TEMP = 22, PSAL = 35)
    db.insert("profile",  station_id = 2, PRES = 4, TEMP = 20, PSAL = 35)
    db.insert("profile",  station_id = 2, PRES = 5, TEMP = 21, PSAL = 35)
    db.insert("profile",  station_id = 2, PRES = 6, TEMP = 22, PSAL = 35)
    db.insert("profile",  station_id = 2, PRES = 7, TEMP = 21.5, PSAL = 35)
    db.insert("profile",  station_id = 2, PRES = 7, TEMP = 21.5, PSAL = 35)

    print('Display join from station an profile tables')
    column = "id"
    # select profile join station 
    result_set = db.select('profile',  {"station_id": 2},'station' )
    for result in result_set:   
        print(result)

    print('get sizes:')
    st = db.query('SELECT COUNT(id) FROM station')
    max_press = db.query('SELECT MAX(PRES) FROM profile')
    print(st, max_press)

if __name__ == "__main__": main()