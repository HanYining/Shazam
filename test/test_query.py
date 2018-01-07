from shazam import query
import unittest
import numpy as np


class Test_cal_match_score(unittest.TestCase):

    def test_match_score(self):
        matching_arr = np.array([[(1, "hello", 3),
                                 (1, "hello", 7)],
                                 [(2, "test", 3),
                                 (1, "hello", 4)],
                                 [(3, "tango", 2),
                                 (1, "hello", 5)]])
        fading_parameter = 0.8
        score, name = query.cal_match_score(matching_arr,
                                            fading_parameter)

        self.assertEqual(score, (1+1.6)/3)
        self.assertEqual(name, "hello")

    def test_setup_lsh(self):
        center, query_obj = query.setup_lsh()
        self.assertEqual(center.shape[0], 25)


if __name__ == '__main__':

    unittest.main()
