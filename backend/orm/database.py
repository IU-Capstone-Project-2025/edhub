from typing import Tuple, Dict, Any, List
import psycopg2


class Database:
    _host: str
    _port: str
    _name: str
    _passwd: str
    _user: str

    def __init__(self, host: str, port: str, name: str, user: str, passwd: str):
        self._host = host
        self._port = port
        self._name = name
        self._passwd = passwd
        self._user = user

    def connection(self) -> psycopg2.extensions.connection:
        return psycopg2.connect(dbname=self._name, user=self._user, password=self._passwd,
                                host=self._host, port=self._port)


class Cursor:
    _cursor: psycopg2.extensions.cursor

    def __init__(self, connection: psycopg2.extensions.connection):
        self._cursor = connection.cursor()

    def __enter__(self):
        self._cursor.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._cursor.__exit__(exc_type, exc_value, exc_traceback)

    def request_fields_all_matches(self, table: str, after_where: str, where_args: tuple, *fields: str) -> List[tuple]:
        self.execute(f"SELECT {', '.join(fields)} FROM {table} WHERE {after_where}", where_args)
        return self._cursor.fetchall()

    def request_fields_one_match(self, table: str, after_where: str, where_args: tuple, *fields: str) -> tuple:
        self.execute(f"SELECT {', '.join(fields)} FROM {table} WHERE {after_where} LIMIT 1", where_args)
        return self._cursor.fetchone()

    def request_field(self, table: str, after_where: str, where_args: tuple, field: str) -> Any:
        return self.request_fields_one_match_cursor(table, after_where, where_args, (field,))[0]

    def execute(self, query: str, query_params: tuple):
        self._cursor.execute(query, query_params)

    def fetchone(self) -> tuple:
        return self._cursor.fetchone()

    def fetchall(self) -> tuple:
        return self._cursor.fetchall()

    def fetchmany(self, count: int) -> tuple:
        return self._cursor.fetchmany(count)

    def exists_custom(self, table: str, after_where: str, where_args: tuple) -> bool:
        self.execute(f"SELECT EXISTS(SELECT 1 FROM {table} WHERE {after_where})", where_args)
        return self.fetchone()[0]

    def exists(self, table: str, **fields: Any) -> bool:
        items = fields.items()
        return self.exists_custom(table, " AND ".join(f"{i[0]} = %s" for i in items), tuple(i[1] for i in items))

    def delete_custom(self, table: str, after_where: str, where_args: tuple):
        self.execute(f"DELETE FROM {table} WHERE {after_where}", where_args)

    def delete(self, table: str, **where: Any):
        items = where.items()
        self.delete_custom(table, " AND ".join(f"{i[0]} = %s" for i in items), tuple(i[1] for i in items))


class DBFieldChanges:
    _newfields: Dict[str, Any]
    _customsets: List[str]

    def __init__(self):
        self._newfields = {}
        self._customsets = []

    def change_any_field(self, field: str, value: Any):
        self._newfields[field] = value
        return self

    def add_custom_update(self, assignment: str):
        self._customsets.append(assignment)

    def compile_update(self, table: str, after_where: str, params_after_where: Tuple[Any]) -> Tuple[str, Tuple[Any]]:
        items = self._newfields.items()
        updates = [f"{i[0]} = %s" for i in items]
        updates.extend(self._customsets)
        return f"UPDATE {table} SET {", ".join(updates)} WHERE {after_where}", \
            tuple(i[1] for i in items) + params_after_where

    def copy(self) -> "DBFieldChanges":
        res = DBFieldChanges()
        res.copy_from(self)
        return res

    def copy_from(self, other_changes: "DBFieldChanges"):
        self._newfields = other_changes._newfields.copy()
        self._customsets = other_changes._customsets.copy()


sysdb = Database("db", "5432", "edhub", "postgres", "12345678")
