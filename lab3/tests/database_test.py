import os
import tempfile

import pytest
from database.database import ClientTable, Database, DepartmentTable, EmployeeTable


@pytest.fixture
def temp_employee_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(b"id,dept_id,name,age,salary\n")
        temp_file.write(b"1,11,Carl,23,25000\n")
        temp_file.write(b"2,12,Lily,20,18000\n")
        temp_file.close()
        yield temp_file.name
    os.remove(temp_file.name)


@pytest.fixture
def temp_department_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(b"dept_id,dept_name\n")
        temp_file.write(b"11,IT\n")
        temp_file.write(b"12,Marketing\n")
        temp_file.close()
        yield temp_file.name
    os.remove(temp_file.name)


@pytest.fixture
def temp_client_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(b"client_id,name,email,phone,address,points,emp_id\n")
        temp_file.write(b"1,Alice,alice@email.com,1234567890,NY,100,12\n")
        temp_file.write(b"2,Bob,bob@email.com,0987654321,CA,150,12\n")
        temp_file.close()
        yield temp_file.name
    os.remove(temp_file.name)


@pytest.fixture
def database(temp_employee_file, temp_department_file, temp_client_file):
    db = Database()
    db._tables.clear()
    emp_table = EmployeeTable(temp_employee_file)
    emp_table.load()
    dept_table = DepartmentTable(temp_department_file)
    dept_table.load()
    client_table = ClientTable(temp_client_file)
    client_table.load()

    db.register_table("employees", emp_table)
    db.register_table("departments", dept_table)
    db.register_table("clients", client_table)

    return db


def test_insert_and_select(database):
    db = database
    db.insert_record("employees", "3 13 Michael 33 43000")
    db.insert_record("departments", "13 HR")
    db.insert_record("clients", "3 Mario mario@email.com 2345678901 CA 200")
    records = db.select_records("employees", 2, 3)
    db.select_records("departments", "HR")
    db.select_records("clients", 50)
    assert len(records) == 2
    names = {record["name"] for record in records}
    assert "Michael" in names


def test_join(database):
    db = database
    joined = db.join_tables("employees", "departments", "dept_id", "dept_id")
    assert len(joined) == 2
    dept_names = {record["dept_name"] for record in joined}
    assert dept_names == {"IT", "Marketing"}
    with pytest.raises(ValueError, match="Одна из таблиц отсутствует."):
        db.join_tables("employees", "unknown_table", "dept_id", "dept_id")


def test_multi_join(database):
    db = database
    joined = db.multi_join(
        ["employees", "departments", "clients"],
        [("dept_id", "dept_id"), ("dept_id", "emp_id")],
    )
    assert len(joined) == 2
    client_names = {record["name"] for record in joined}
    assert client_names == {"Alice", "Bob"}


def test_multi_join_invalid_conditions(database):
    db = database
    with pytest.raises(
        ValueError, match="Число условий должно быть на одно меньше количества таблиц."
    ):
        db.multi_join(["employees", "departments", "clients"], [("dept_id", "dept_id")])

    with pytest.raises(ValueError, match="Таблица 'unknown_table' не найдена."):
        db.multi_join(["employees", "unknown_table"], [("dept_id", "dept_id")])


def test_aggregate(database):
    db = database
    avg_salary = db.aggregate("employees", "avg", "salary")
    max_salary = db.aggregate("employees", "max", "salary")
    min_salary = db.aggregate("employees", "min", "salary")
    assert avg_salary == 21500.0
    assert max_salary == 25000.0
    assert min_salary == 18000.0
    with pytest.raises(ValueError, match="Таблица 'unknown_table' не найдена."):
        db.aggregate("unknown_table", "avg", "asd")


def test_duplicate_insert(database):
    db = database
    with pytest.raises(ValueError, match="Запись уже существует"):
        db.insert_record("employees", "1 11 Carl 35 45000")


def test_invalid_aggregation(database):
    db = database
    with pytest.raises(ValueError, match="Неизвестная операция 'sum'."):
        db.aggregate("employees", "sum", "salary")
    with pytest.raises(ValueError, match="Таблица 'unknown_table' не найдена."):
        db.aggregate("unknown_table", "sum", "salary")


def test_errors(database):
    db = database
    with pytest.raises(ValueError, match="Таблица 'employees' уже зарегистрирована."):
        db.register_table("employees", 123)
    with pytest.raises(ValueError, match="Таблица 'unknown_table' не найдена."):
        db.insert_record("unknown_table", "asdasd")
    with pytest.raises(ValueError, match="Таблица 'unknown_table' не найдена."):
        db.select_records("unknown_table", 123)
