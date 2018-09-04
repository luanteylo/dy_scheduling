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


def insert_task(conn, job_id, task_id, name, memory, io_size):

    sql = ''' INSERT INTO tasks(job_id, task_id, name, memory, io_size)  VALUES(?, ?, ?, ?, ?) '''

    try:
        cur = conn.cursor()
        cur.execute(sql, (job_id, task_id, name, memory, io_size))
    except sqlite3.Error as e:
        print e


def insert_execution(conn, job_id, task_id, run_id, type, runtime, status="sucess"):

    sql = ''' INSERT INTO execution(job_id, task_id, run_id, type, runtime, status)  VALUES (?, ?, ?, ?, ?, ?) '''

    try:
        cur = conn.cursor()
        cur.execute(sql, (job_id, task_id, run_id,  type, runtime, status))
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


def update_price(conn, type, market, region, price, zone=None):
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


def select_job(conn, job_id):

    rows = []

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks where job_id = ?", (job_id,))
        rows = cur.fetchall()
    except sqlite3.Error as e:
        print e

    return rows


def select_execution(conn, run_id):
    rows = []

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM execution where run_id = ?", (run_id,))
        rows = cur.fetchall()
    except sqlite3.Error as e:
        print e

    return rows


def select_instance(conn, type):
    rows = []

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM instances where type = ?", (type,))
        rows = cur.fetchall()
    except sqlite3.Error as e:
        print e

    return rows


def select_instance_price(conn, type, market, region, zone=None):
    sql = ""
    tpl = None

    if market == 0:  # ondemand
        sql = '''
            SELECT * FROM prices where type = ? and region = ? and  market = ?        
            '''
        tpl = (type, region, market)
    else:  # spot
        sql = '''
            SELECT * FROM prices where type = ? and region = ? and  market = ? and zone = ?        
            '''
        tpl = (type, region, market, zone)

    # print sql, tpl

    try:
        cur = conn.cursor()
        cur.execute(sql, tpl)
        rows = cur.fetchall()
    except sqlite3.Error as e:
        print e

    return rows

def select_runtime(conn, job_id, task_id, type):
    sql = ''' select avg(runtime) from execution where job_id = ? and task_id =  ? and type = ?'''

    try:
        cur = conn.cursor()
        cur.execute(sql, (job_id, task_id, type))
        rows = cur.fetchall()
    except sqlite3.Error as e:
        print e

    return rows[0][0]

def select_all_instance(conn):
    """
        Query all rows in the instance table
        :param conn: the Connection object
        :return:
        """
    cur = conn.cursor()
    cur.execute("SELECT * FROM instances")

    rows = cur.fetchall()

    return rows


def select_all_job_instances(conn, job_id):
    sql = '''select DISTINCT instances.type  from execution, instances where execution.job_id = ? and execution.type = instances.type'''

    try:
        cur = conn.cursor()
        cur.execute(sql, (job_id,))
        rows = cur.fetchall()
    except sqlite3.Error as e:
        print e

    return rows


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
