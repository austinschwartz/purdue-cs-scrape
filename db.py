import psycopg2

class DB:
    def __init__(self, user, password):
        connect_str = "dbname='purduecs' user='" + user + "' host='localhost' " + "password='" + password + "'"
        self.conn = psycopg2.connect(connect_str)
        #self.create()

    def create(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""DROP TABLE IF EXISTS sections""")
            cursor.execute("""
            CREATE TABLE sections (
                crn         char(5) CONSTRAINT firstkey PRIMARY KEY,
                title       varchar(64) NOT NULL,
                number      varchar(64) NOT NULL,
                term        varchar(32) NOT NULL,
                type        varchar(32) NOT NULL,
                time        varchar(64) NOT NULL,
                days        varchar(16) NOT NULL,
                location    varchar(128) NOT NULL,
                date_range  varchar(64) NOT NULL,
                schedule_type varchar(64) NOT NULL,
                instructors  varchar(64) NOT NULL
            );
            """)
            self.conn.commit()
        except Exception as e:
            print("Can't connect for some reason: ", e)

    def insert(self, section):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO sections (crn, title, number, term, type, time, days, location, date_range, schedule_type, instructors) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on conflict (crn) do nothing;", (section.crn, section.title, section.number, section.term, section.type, section.time, section.days, section.where, section.date_range, section.schedule_type, section.instructors))
        self.conn.commit()

    def print_rows(self):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT * from sections""")
        rows = cursor.fetchall()
        print(rows)

    

