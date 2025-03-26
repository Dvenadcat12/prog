import csv
import os
from abc import ABC, abstractmethod


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):

    def __init__(self):
        self._tables = {}

    def register_table(self, table_name, table):
        if table_name in self._tables:
            raise ValueError(f"Таблица '{table_name}' уже зарегистрирована.")
        self._tables[table_name] = table

    def insert_record(self, table_name, record):
        table = self._tables.get(table_name)
        if not table:
            raise ValueError(f"Таблица '{table_name}' не найдена.")
        table.add_entry(record)

    def select_records(self, table_name, *criteria):
        table = self._tables.get(table_name)
        if not table:
            raise ValueError(f"Таблица '{table_name}' не найдена.")
        return table.search(*criteria)

    def join_tables(self, table1, table2, key1, key2):
        if table1 not in self._tables or table2 not in self._tables:
            raise ValueError("Одна из таблиц отсутствует.")

        left_records = self._tables[table1].entries
        right_records = self._tables[table2].entries

        return [
            {**left, **right}
            for left in left_records
            for right in right_records
            if left.get(key1) == right.get(key2)
        ]

    def multi_join(self, tables, conditions):
        if len(conditions) != len(tables) - 1:
            raise ValueError(
                "Число условий должно быть на одно меньше количества таблиц."
            )

        result = self._tables[tables[0]].entries

        for i, table in enumerate(tables[1:], start=1):
            if table not in self._tables:
                raise ValueError(f"Таблица '{table}' не найдена.")
            key1, key2 = conditions[i - 1]
            result = [
                {**rec1, **rec2}
                for rec1 in result
                for rec2 in self._tables[table].entries
                if rec1.get(key1) == rec2.get(key2)
            ]

        return result

    def aggregate(self, table_name, operation, column):
        table = self._tables.get(table_name)
        if not table:
            raise ValueError(f"Таблица '{table_name}' не найдена.")

        values = [float(row[column]) for row in table.entries if column in row]

        operations = {
            "avg": lambda v: sum(v) / len(v),
            "max": max,
            "min": min,
            "count": len,
        }

        if operation not in operations:
            raise ValueError(f"Неизвестная операция '{operation}'.")

        return operations[operation](values)


class BaseTable(ABC):

    def __init__(self, file_path):
        self.file_path = file_path
        self.entries = []
        self.load()

    @abstractmethod
    def columns(self):  # pragma: no cover
        pass

    @abstractmethod
    def primary_key(self, entry):  # pragma: no cover
        pass

    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, mode="r", newline="") as file:
                reader = csv.DictReader(file)
                self.entries = list(reader)
        else:  # pragma: no cover
            self.entries = []

    def save(self):
        with open(self.file_path, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.columns())
            writer.writeheader()
            writer.writerows(self.entries)

    def add_entry(self, data):
        values = data.split()
        new_entry = dict(zip(self.columns(), values))

        if any(
            self.primary_key(row) == self.primary_key(new_entry) for row in self.entries
        ):
            raise ValueError(f"Запись уже существует: {new_entry}")

        self.entries.append(new_entry)
        self.save()


class EmployeeTable(BaseTable):
    def columns(self):
        return "id", "dept_id", "name", "age", "salary"

    def primary_key(self, entry):
        return entry["id"], entry["dept_id"]

    def search(self, min_id, max_id):
        return [row for row in self.entries if min_id <= int(row["id"]) <= max_id]


class DepartmentTable(BaseTable):
    def columns(self):
        return "dept_id", "dept_name"

    def primary_key(self, entry):
        return entry["dept_id"]

    def search(self, dept_name):
        return [row for row in self.entries if row["dept_name"] == dept_name]


class ClientTable(BaseTable):
    def columns(self):
        return "client_id", "name", "email", "phone", "address", "points", "emp_id"

    def primary_key(self, entry):
        return entry["client_id"]

    def search(self, min_points):
        return [row for row in self.entries if int(row["points"]) > min_points]
