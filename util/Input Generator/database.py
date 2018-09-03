import sqlite3

from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def insert_instance(conn, type, memory, vcpu):
    sql = ''' INSERT INTO instances(type, memory, vcpu)  VALUES(?, ?, ?) '''

    try:
        cur = conn.cursor()
        cur.execute(sql, (type, memory, vcpu))
    except sqlite3.Error as e:
        print e


def insert_price(conn, type, market, region, price, zone=None):
    sql = ""
    tpl = None

    if market == 0:  # ondemand
        sql = '''
        INSERT INTO prices(type, market, region, price)  VALUES(?, ?, ?, ?)        
        '''
        tpl = (type, market, region, price)
    else:  # spot
        sql = '''
        INSERT INTO prices(type, market, region, zone, price)  VALUES(?, ?, ?, ?, ?)
        '''
        tpl = (type, market, region, zone, price)

    print sql, tpl

    try:
        cur = conn.cursor()
        cur.execute(sql, tpl)
    except sqlite3.Error as e:
        print e


def update_price(conn, type, market, region, price, zone):
    sql = ""
    tpl = None

    if market == 0:  # ondemand
        sql = '''
           UPDATE prices
           SET price = ? WHERE type = ? and market = ? and region = ?        
           '''
        tpl = (price, type, market, region)
    else:  # spot
        sql = '''
           UPDATE prices
           SET price = ? where type = ? and market = ? and region = ? and zone = ?
           '''
        tpl = (price, type, market, region, zone)

    try:
        cur = conn.cursor()
        cur.execute(sql, tpl)
    except sqlite3.Error as e:
        print e


def select_all_instance(conn):
    """
        Query all rows in the instance table
        :param conn: the Connection object
        :return:
        """
    cur = conn.cursor()
    cur.execute("SELECT * FROM instances")

    rows = cur.fetchall()

    for row in rows:
        print(row)


def delete_instance(conn, type):
    sql = ''' DELETE FROM instances WHERE type = ?  '''

    try:
        cur = conn.cursor()
        cur.execute(sql, (type,))
    except sqlite3.Error as e:
        print e

#
# Test
# conn = create_connection("db.bin")
# with conn:
#     delete_instance(conn, "hello")
#     select_all_instance(conn)
