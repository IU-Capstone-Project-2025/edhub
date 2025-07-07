import itertools
import csv


def encode_to_csv(rows, columns, content: list[list]) -> str:
    with csv.StringIO() as stream:
        writer = csv.writer(stream, dialect="excel")
        writer.writerow(itertools.chain((None,), columns))
        for email, line in zip(rows, content):
            writer.writerow(itertools.chain((email,), line))
        return stream.getvalue()
