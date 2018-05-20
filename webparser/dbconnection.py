import sqlite3

import sys

from webparser import websettings

class DataBaseError(Exception):
    pass


def run_sql(sql, params=None):
    try:
        conn = sqlite3.connect(websettings.DB_NAME)
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(sql)
        print(sys.exc_info()[1])
        print(sys.exc_info()[2])
        raise DataBaseError()
    else:
        if cursor.arraysize == 1:
            return cursor.fetchone()
        else:
            return cursor.fetchall()
