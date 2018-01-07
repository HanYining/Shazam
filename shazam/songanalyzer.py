# Yining Han
# Shazam !

import re
import numpy as np
from scipy import signal
import wave
import pyaudio
import glob
import psycopg2

# windowing methods to analyze and read in the data sets
# average over the left and right stereo, get a time series data
# get some set window length, which is the minimum required length
# of any recognizeable snippet.
# Here it may require further parameter tuning methods


def peakpicker(spectrogram, framerate, freq_portion):
    """
    for simplicity here, we assume the discrete fourier transformation
    returns the same amount of frequency structures
    aka fingerprinter, to compute the signature
    go for an easy solution first, get the peak values among
    windowed frequency.

    Args:
        spectrogram: the spectrogram of a song/collection, with row as
                     frequency value and column as time.
        framerate: the sampling frequency of the song/collection,one limitation
                   here is that this program currently does not support
                   Songs with different sampling frequency
        freq_portion: the length of the local neighborhood we choose to
                      get the local peaks.

    Returns:
        peaks: which is a nparray representing the low dimensional signature
               of the spectrogram.
    """
    peak_lst = []
    local_len = int(freq_portion*framerate)
    for row in spectrogram:
        peak_row = []
        for i in range(len(row) // local_len):
            sub_periodgram = row[i * local_len:min(
                len(row), (i + 1) * local_len)]
            max_loc = np.argmax(sub_periodgram)
            peak_row.append(max_loc + i*local_len)
        peak_lst.append(peak_row)
    return np.array(peak_lst)


def readin_singlesong(file_loc, window_methods, window_len, shift_step, freq_portion):
    """
    This is the function provided to support the analyze of a single song.
    It generate the required signature for one song.

    Args:
        file_loc: the physical location of the file on PC
        window_methods: a string representing the window methods used to
                        generate the corresponding window data.
        window_len: the time length of the window data.
        shift_step: the time length of the shifting step between windows.
        freq_portion: the local length in which the peaks are selected.

    Returns:
        signature: the low dimensional signature representation of the song.
    """
    file = wave.open(file_loc)

    audio = pyaudio.PyAudio()
    audio.open(
        format=audio.get_format_from_width(file.getsampwidth()),
        channels=file.getnchannels(),
        rate=file.getframerate(),
        output=True)

    nframes = file.getnframes()
    framerate = file.getframerate()
    stringData = file.readframes(nframes)

    file.close()

    audioary = np.fromstring(stringData, dtype=np.short)
    audioary.shape = -1, 2
    audioary = np.mean(audioary.T, axis=0)

    f, t, spec = signal.spectrogram(
        audioary,
        fs=framerate,
        nperseg=window_len * framerate,
        noverlap=(window_len - shift_step) * framerate,
        window=window_methods)

    akafinger_printer = peakpicker(spec.T, framerate, freq_portion)

    return akafinger_printer


def insert_singlesong(akafingerprint, song_name, window_len, shift_step):
    """
    Since we support full directory digest. The way we digest a single song is
    different from the whole directory digest, it support user defined song name

    Args:
        akafingerprint: the signature matrix computed from readsinglesong
        song_name; the user input of the song's name.
        window_len: the time length user choose to set up the signature for
                    the database, not sure if need to change yet. But it is
                    surely required to generate the accurate time center for
                    each window.
        shift_step: the amount of time shift between two consecutive windows.

    Returns:
        A notice if the song is the song is successfully inserted.
        Or error message if the song already exists in the database.

    Raises:
        Possible duplicates needs to be handled with exception.
    """
    TIME_ID = window_len//2

    conn = psycopg2.connect("dbname=yinhan user=yinhan")
    cursor = conn.cursor()

    sqlcmd = "INSERT INTO SONGS VALUES (DEFAULT, %s)"
    try:
        cursor.execute(sqlcmd, (song_name,))
    except psycopg2.Error as e:
        conn.rollback()
        print("Duplicated Song {0} Skipped!".format(song_name))
    else:
        cursor.execute("SELECT MAX(SONG_ID) FROM SONGS")
        NEXT_SONG_ID = cursor.fetchone()[0]
        for row in akafingerprint:
            sqlcmd = "INSERT INTO AKAFINGER VALUES (DEFAULT, %s, %s, %s);"
            cursor.execute(sqlcmd, (TIME_ID, NEXT_SONG_ID, row.tolist()))
            TIME_ID += shift_step
        print("Successfully inserted "+song_name)
        conn.commit()
    finally:
        conn.close()

    pass


def digest_music(locations, window_methods, window_len, shift_step, freq_portion):
    """
    This is the function provided to support the analyze a whole directory
    of songs. It generate the required signature for all songs.

    Args:
        file_loc: the physical location of the file on PC
        window_methods: a string representing the window methods used to
                        generate the corresponding window data.
        window_len: the time length of the window data.
        shift_step: the time length of the shifting step between windows.
        freq_portion: the local length in which the peaks are selected.

    Returns:
        signature: the low dimensional signature representation of the songs.
        name_loc: which is a location saver with the song's name as its key and
                  the song's corresponding window data's maximum row number in
                  the signature matrix. which is useful when inserting songs
                  into database and retain the linkage between songs and windows.
    """
    file_locs = glob.glob(locations)

    for i, file_loc in enumerate(file_locs):
        filenames = re.sub("^[^a-zA-Z]+([a-zA-Z ']+).*$", "\\1", file_loc.split("/")[-1])

        aka_fingprinter = readin_singlesong(file_loc, window_methods, window_len, shift_step, freq_portion)

        insert_singlesong(aka_fingprinter, filenames, window_len, shift_step)

    return
