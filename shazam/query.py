# User interface to connect with the music db
# to do: get the snippet data.
import numpy as np
import psycopg2
import falconn


def setup_lsh():

    # extract the signature matrix from database

    con = psycopg2.connect("dbname=yinhan user=yinhan")
    cur = con.cursor()
    cur.execute("SELECT SIGNATURE FROM AKAFINGER")
    lst = cur.fetchall()
    con.commit()
    con.close()

    data = np.array([val[0] for val in lst])
    center = np.mean(data, axis=0)
    data = data-center
    # use the center of the data base to center snippet
    # allegedly to improve the model performance
    params_cp = falconn.get_default_parameters(num_points=data.shape[0],
                                               dimension=data.shape[1])
    table = falconn.LSHIndex(params_cp)
    table.setup(data)

    return center, table.construct_query_object()


def cal_match_score(matching_array, fading_parameter):
    """
    fading parameter is a way to utilize the matching information
    in the returned falconn K nearest matches, when the song of
    interest is not matched as the top one. The following non-top
    matches are still counted with an exponentially fading factor
    with its relative rank.

    Args:
        matching_array: The K nearest matching information for every window
                        based on the falconn
        fading_parameter: The fading parameter decide how harsh we punish
                          an imperfect match (possibly wrong match)
                          it should be in the range of (0,1)

    Return:
        best_match_score: a matching score based on the rank of the
                          chosen song in the K falconn nearest neighbors
                          the score is normalized to range(0, 1)
        best_match_songname: The best matching song's name
    """

    # fading parameter is a way to utilize the information if the
    # 2nd or 3rd .. best matches for a single windowed data.


    consecutive_counter = {}

    for snippet_candidates in matching_array:
        rank = 0
        checker = set()
        for single_candidate in snippet_candidates:
            song_id, song_name, time_id = single_candidate
            if song_name in checker:
                continue
            checker.add(song_name)
            if song_name not in consecutive_counter.keys():
                consecutive_counter[song_name] = fading_parameter**rank
            else:
                consecutive_counter[song_name] += fading_parameter**rank
            rank += 1

    best_match_songname = max(consecutive_counter, key=consecutive_counter.get)
    best_match_score = consecutive_counter[best_match_songname]/len(matching_array)

    return best_match_score, best_match_songname


def find_best_match(query, snippet, center, K):
    """
    This is an attempt to query the snippet and return the
    possible best matches. If no matches are found above 70%
    confidence. Then a notice is throw.

    Args:
        query: a query object from the flaconn library which
               is constructed by the setLSH function.
        snippet: the snippet provided by the user, which should
                 have a minimum length of 10 seconds.
        center: the mean of the song signature data base, this is
                said to increase the efficiency and performance of
                falconn LSH.
        K: the number of nearest neighbor returned by the falconn.
           Presumablly, the bigger K is, the more robust the algorithm
           should be and the better the algorithm would be to find
           blurry songs.

    Returns:
        Now it is a string represent the song's name or a notice of
        no matches available when none is found with high confidence
        Maybe need to add more info about the song, etc album years
        stuffs like that and do formatted printout.

    Raises:
        the input snippet has to be at least 10 seconds long, snippet
        less than that might cause error in the falconn matching process.
    """

    # fading parameter is a way to utilize the information if the
    # 2nd or 3rd .. best matches for a single windowed data.

    fading_parameter = 0.5
    matches = []
    for row in snippet:
        row = row.astype(np.float32)
        matches.append(query.find_k_nearest_neighbors(row-center, K))

    conn = psycopg2.connect("dbname=yinhan user=yinhan")
    cur = conn.cursor()

    match_id = []
    for id_lst in matches:
        matching_window = []
        for id in id_lst:
            sqlcmd = """SELECT AKAFINGER.SONG_ID, SONG_TITLE,
                           TIME_ID
                           FROM AKAFINGER LEFT JOIN SONGS
                           ON AKAFINGER.SONG_ID = SONGS.SONG_ID
                           WHERE AKAFINGER.SIGNATURE_ID = %s"""
            cur.execute(sqlcmd, [id])
            matching_window += cur.fetchall()
        match_id.append(matching_window)

    conn.commit()
    conn.close()

    best_match_score, best_match_songname = cal_match_score(match_id, fading_parameter)

    if best_match_score < 0.7:
        print("We have no matches in the repository!")
        return False

    print("The song you are looking for is {0} with confidence {1}%".format(
        best_match_songname, 100*best_match_score))

    return best_match_songname
