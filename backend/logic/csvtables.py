import itertools
import csv


def encode_to_csv(content: list[list]) -> str:
    with csv.StringIO() as stream:
        writer = csv.writer(stream, dialect="excel")
        writer.writerows(content)
        return stream.getvalue()


def encode_to_csv_with_columns(columns: list, content: list[list]) -> str:
    with csv.StringIO() as stream:
        writer = csv.writer(stream, dialect="excel")
        writer.writerow(columns)
        writer.writerows(content)
        return stream.getvalue()


def encode_to_csv_with_rows_columns(rows, columns, content: list[list]) -> str:
    with csv.StringIO() as stream:
        writer = csv.writer(stream, dialect="excel")
        writer.writerow(itertools.chain((None,), columns))
        for email, line in zip(rows, content):
            writer.writerow(itertools.chain((email,), line))
        return stream.getvalue()
