import psycopg2


def create_table():
    """
    A function that creates table in local computer
    Note that ideally the function should only be called once.

    """
    connect = psycopg2.connect("dbname=yinhan user=yinhan")
    cursor = connect.cursor()

    cursor.execute("DROP TABLE IF EXISTS AKAFINGER")
    cursor.execute("DROP TABLE IF EXISTS SONGS")
    connect.commit()

    cursor.execute("CREATE TABLE SONGS ( SONG_ID SERIAL PRIMARY KEY, SONG_TITLE VARCHAR(40) UNIQUE)")
    cursor.execute("""CREATE TABLE AKAFINGER ( SIGNATURE_ID SERIAL PRIMARY KEY,
                                               TIME_ID INTEGER,
                                               SONG_ID INTEGER REFERENCES SONGS(SONG_ID),
                                               SIGNATURE FLOAT[]
                                              )""")
    connect.commit()

    connect.close()

    return
