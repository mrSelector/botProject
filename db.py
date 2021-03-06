import sqlite3
from typing import Dict, List, Tuple

conn = sqlite3.connect("finance.db")
cursor = conn.cursor()


def insert(table: str, column: Dict):
    columns = ', '.join(column.keys())
    values = [tuple(column.values())]
    placeholders = ", ".join("?" * len(column.keys()))
    # print(placeholders)
    cursor.executemany(
        f'INSERT INTO {table}'
        f'({columns})'
        f'VALUES ({placeholders})',
        values)
    conn.commit()


def fetchall(table: str, columns: List[str]) -> List[Tuple]:
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def delete(table: str, row_id: int) -> None:
    row_id = int(row_id)
    cursor.execute(f"delete from {table} where id={row_id}")
    conn.commit()


def get_cursor():
    return cursor
