import psycopg2
import unittest
from shazam import songanalyzer
from shazam import dbconstruct
import numpy as np


class Test_insert_song(unittest.TestCase):

    def test_insertion(self):
        dbconstruct.create_table()
        akafinger = np.random.rand(1000, 25)
        # try an insertion capture error type
        try:
            songanalyzer.insert_singlesong(akafinger, "testing fake song",
                                           10, 1)
        except ExceptionType:
            self.fail("The function Insert_Singlesong failed with {0}".format(ExceptionType))

    def test_select(self):
        # test for the results of insertion
        connect = psycopg2.connect("dbname=yinhan user=yinhan")
        cursor = connect.cursor()
        cursor.execute("select exists(select * from songs where song_title=%s)", ('testing fake song',))
        self.assertTrue(cursor.fetchone()[0])

        cursor.execute("""select exists(select * from akafinger where song_id =(select song_id from songs where song_title = %s))""", ("testing fake song",))
        self.assertTrue(cursor.fetchone()[0])

    def test_get_exact_insert(self):
        # randomly generate a song matrix
        dbconstruct.create_table()
        akafinger = np.random.rand(1000, 25)
        songanalyzer.insert_singlesong(akafinger, "testing fake song",
                                       10, 1)
        # the random signature I inserted should be the same when I extract
        connect = psycopg2.connect("dbname=yinhan user=yinhan")
        cursor = connect.cursor()
        cursor.execute("""select SIGNATURE from AKAFINGER""")
        lst = cursor.fetchall()
        connect.close()

        self.assertTrue(np.isclose(np.array([val[0] for val in lst]), akafinger).all())


if __name__ == '__main__':

    unittest.main()
