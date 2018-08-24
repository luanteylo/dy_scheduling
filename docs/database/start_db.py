import sqlite3


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)

    return None






def create_market(conn, market_type):
    """
    Create a new market type into the marketType table
    :param conn:
    :param market_type:
    :return:
    """
    sql = ''' INSERT INTO marketType(name)
              VALUES(?) '''
    cur = conn.cursor()
    cur.execute(sql, market_type)
    return cur.lastrowid


def create_status(conn, status_list):
    """
    Create a new status type into the status table
    :param conn:
    :param market_type:
    :return:
    """
    # sql = ''' INSERT INTO status(name)
    #           VALUES(?) '''
    sql = ''' UPDATE status SET name = ? WHERE id=7 '''
    cur = conn.cursor()
    for status in status_list:
        cur.execute(sql, (status,))

    return cur.lastrowid


conn = create_connection("db.bin")

with conn:
    create_status(conn, [""])






