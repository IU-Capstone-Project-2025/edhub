import csv


def encode_to_csv_with_columns(columns: list, content: list[list]) -> str:
    with csv.StringIO() as stream:
        writer = csv.writer(stream, dialect="excel")
        writer.writerow(columns)
        writer.writerows(content)
        return stream.getvalue()
