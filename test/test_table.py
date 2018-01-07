import psycopg2
import unittest


class Test_construct_table(unittest.TestCase):

    def test_table_exist(self):
        connect = psycopg2.connect("dbname=yinhan user=yinhan")
        cursor = connect.cursor()
        cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", ('songs',))
        self.assertTrue(cursor.fetchone()[0])
        cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", ('akafinger',))
        self.assertTrue(cursor.fetchone()[0])
        connect.commit()
        connect.close()

if __name__ == '__main__':

    unittest.main()

