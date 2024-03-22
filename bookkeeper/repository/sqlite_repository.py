from bookkeeper.repository.abstract_repository import AbstractRepository, T
import inspect

import sqlite3

class SQliteRepository(AbstractRepository[T]):
    """
    Репозиторий, работающий в ??. ??
    """

    def __init__(self, base_name: str, class_type: type) -> None:
        self._base_name = base_name
        self._table_name = class_type.__name__
        self._fields = inspect.get_annotations(class_type, eval_str=True)
        self._fields.pop('pk')
