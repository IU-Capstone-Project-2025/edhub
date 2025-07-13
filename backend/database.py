from psycopg2.pool import PoolError
from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool

import edhub_errors


def mk_database(dbname, user, password, host, port):

    # TODO: set minconn maxconn in some options? perhaps environment variables?
    conn_pool = ThreadedConnectionPool(
        minconn=2, maxconn=20, dbname=dbname, user=user, password=password, host=host, port=port
    )

    @contextmanager
    def get_conn():
        conn = None
        try:
            conn = conn_pool.getconn()
            yield conn
        except PoolError:
            raise edhub_errors.PoolFullException()
        finally:
            if conn:
                conn.commit()
                conn_pool.putconn(conn)

    return get_conn


get_system_conn = mk_database(dbname="edhub", user="postgres", password="12345678", host="system_db", port="5432")

get_storage_conn = mk_database(
    dbname="edhub_storage", user="postgres", password="12345678", host="filestorage_db", port="5432"
)
