from bookkeeper.repository.abstract_repository import AbstractRepository, T
import inspect
from typing import Any

import sqlite3


class SQliteRepository(AbstractRepository[T]):
    """
    Репозиторий, работающий в ??. ??
    """

    def __init__(self, base_name: str, class_type: type) -> None:
        self._base_name = base_name
        self._table_name = class_type.__name__
        self._fields = inspect.get_annotations(class_type, eval_str=True)
        self._fields.pop("pk")
        self._class_type = class_type

        with sqlite3.connect(self._base_name) as con:
            cur = con.cursor()
            cur.execute("PRAGMA foreign_keys = ON")
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS {self._table_name}"
                + "(pk INTEGER PRIMARY KEY NOT NULL, "
                + ", ".join(
                    f"{name} {self._py_to_sql(tpy)}"
                    for name, tpy in self._fields.items()
                )
                + ")"
            )
        con.close()

    def _py_to_sql(self, tpy: type) -> str:
        if tpy == int:
            return "INTEGER"
        if tpy == str:
            return "TEXT"
        if tpy == float:
            return "REAL"
        raise ValueError(f"Type {tpy} is not supported")

    def add(self, obj: T) -> int:
        if getattr(obj, "pk", None) != 0:
            raise ValueError("Trying to add object with filled 'pk' attribute")

        names = ", ".join(self._fields)
        placeholders = ", ".join("?" * len(self._fields))

        values = [getattr(obj, key) for key in self._fields]

        with sqlite3.connect(self._base_name) as con:
            cur = con.cursor()
            cur.execute("PRAGMA foreign_keys = ON")
            cur.execute(
                f"INSERT INTO {self._table_name} ({names}) VALUES ({placeholders})",
                values,
            )

            obj.pk = cur.lastrowid

        con.close()

        return obj.pk

    def get(self, pk: int) -> T | None:
        """Получить объект по id"""

        with sqlite3.connect(self._base_name) as con:
            cur = con.cursor()
            cur.execute("PRAGMA foreign_keys = ON")
            cur.execute(f"SELECT * FROM {self._table_name} WHERE pk = {pk}")
            res = cur.fetchone()
        con.close()
        obj = self._class_type()
        setattr(obj, "pk", res[0])
        for i, name in enumerate(self._fields, 1):
            setattr(obj, name, res[i])
        return res

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию), вернуть все записи
        """
        with sqlite3.connect(self._base_name) as con:
            cur = con.cursor()
            cur.execute("PRAGMA foreign_keys = ON")
            if where is None:
                cur.execute(f"SELECT * FROM {self._table_name}")
            else:
                where_keys = list(where.keys())
                where_values = list(where.values())
                text = f"SELECT * FROM {self._table_name} WHERE ({where_keys[0]}) = ({where_values[0]})"
                for i in range(1, len(where)):
                    text += f" AND {where_keys[i]}) = ({where_values[i]})"
                cur.execute(text)
            res = cur.fetchone()
        con.close()
        return res

    def update(self, obj: T) -> None:
        """Обновить данные об объекте. Объект должен содержать поле pk."""
        if getattr(obj, "pk", None) is None:
            raise ValueError("Object does not exist")

        names = ", ".join(self._fields)
        placeholders = ", ".join("?" * len(self._fields))

        values = [getattr(obj, key) for key in self._fields]

        with sqlite3.connect(self._base_name) as con:
            cur = con.cursor()
            cur.execute("PRAGMA foreign_keys = ON")
            cur.execute(
                f"UPDATE {self._table_name} SET ({names}) VALUES ({placeholders}) WHERE pk = {obj.pk}",
                values,
            )


        con.close()

        return None
