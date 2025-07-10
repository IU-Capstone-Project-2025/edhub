import psycopg2
from contextlib import contextmanager


def mk_database(dbname, user, password, host, port):

    @contextmanager
    def get_conn():
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        try:
            yield conn
        finally:
            conn.close()

    return get_conn


get_system_conn = mk_database(dbname="edhub", user="postgres", password="12345678", host="system_db", port="5432")

get_storage_conn = mk_database(
    dbname="edhub_storage", user="postgres", password="12345678", host="storage_db", port="5432"
)
