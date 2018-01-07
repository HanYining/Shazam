import unittest
import numpy as np
from shazam import songanalyzer
from shazam import dbconstruct
from shazam import query


class Test_Analyzesong(unittest.TestCase):

    def test_peakpicker_int(self):
        spectrogram = np.array([[1, 2, 3, 1, 2, 4],
                                [1, 2, 3, 1, 2, 4],
                                [1, 2, 3, 1, 2, 4]])

        framerate = 2
        freq_portion = 1
        signature = songanalyzer.peakpicker(spectrogram, framerate, freq_portion)
        self.assertTrue(np.array_equal(signature, np.array([[1, 2, 5],
                                                            [1, 2, 5],
                                                            [1, 2, 5]])))

    def test_peakpicker_nonint(self):
        spectrogram = np.array([[1, 2, 3, 1, 2],
                                [1, 2, 3, 1, 2],
                                [1, 2, 3, 1, 2]])

        framerate = 2
        freq_portion = 1
        signature = songanalyzer.peakpicker(spectrogram, framerate, freq_portion)
        self.assertTrue(np.array_equal(signature, np.array([[1, 2],
                                                            [1, 2],
                                                            [1, 2]])))

    def test_read_sample_song(self):
        sample_file = songanalyzer.readin_singlesong("/Users/yinhan/testing/test.wav", "hamming", 10, 1, 0.2)
        # Since the sample song has 80000 the spectrogram should be some shape (x, 40000)
        # And since the peak peaker procedure find 50 peaks in a window.
        # thus the akafinger printer obtained through the function should have shape
        # (x, 50)

        self.assertEqual(sample_file.shape[1], 25)

        # since the length of the song is around 3 mins
        # so the row number of the signature matrix is around
        # 300, to make it safe, the test tests weather it is
        # roughly between 200 400

        self.assertTrue(sample_file.shape[0] > 200)
        self.assertTrue(sample_file.shape[0] < 400)

    def test_match_only_song(self):
        dbconstruct.create_table()
        sample_file = songanalyzer.readin_singlesong("/Users/yinhan/testing/test.wav", "hamming", 10, 1, 0.2)
        songanalyzer.insert_singlesong(sample_file, "test", 10, 1)
        center, query_obj = query.setup_lsh()
        name = query.find_best_match(query_obj, sample_file, center, 3)
        self.assertEqual(name, "test")


if __name__ == "__main__":

    unittest.main()
