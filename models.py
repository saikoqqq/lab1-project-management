"""Классы предметной области «Управление проектами».

Каждый объект создаётся вызовом конструктора с именованными аргументами,
например Employee(id=1, name="Иван", ...). Имена аргументов совпадают
с ключами словаря, поэтому объект можно создать из словаря: Employee(**data).
Все значения проверяются в конструкторе. Если значение некорректно,
выбрасывается ValidationError.
"""

from datetime import datetime
from typing import Any

from exceptions import ValidationError

# Допустимые значения статусов и приоритетов
PROJECT_STATUSES = ["planned", "active", "completed"]
TASK_STATUSES = ["todo", "in_progress", "done"]
PRIORITIES = ["low", "medium", "high"]


# ----------------------- Функции проверки значений -----------------------

def check_id(value: Any, field: str) -> int:
    """Проверяет, что значение - целое число больше нуля."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Поле '{field}' должно быть целым числом")
    if number <= 0:
        raise ValidationError(f"Поле '{field}' должно быть больше нуля")
    return number


def check_text(value: Any, field: str) -> str:
    """Проверяет, что строка не пустая."""
    if value is None:
        raise ValidationError(f"Поле '{field}' не может быть пустым")
    text = str(value).strip()
    if not text:
        raise ValidationError(f"Поле '{field}' не может быть пустым")
    return text


def check_number(value: Any, field: str) -> float:
    """Проверяет, что значение - неотрицательное число."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Поле '{field}' должно быть числом")
    if number < 0:
        raise ValidationError(f"Поле '{field}' не может быть отрицательным")
    return number


def check_date(value: Any, field: str) -> str:
    """Проверяет, что строка - дата в формате ГГГГ-ММ-ДД."""
    try:
        datetime.strptime(str(value).strip(), "%Y-%m-%d")
    except ValueError:
        raise ValidationError(f"Поле '{field}' должно быть датой ГГГГ-ММ-ДД")
    return str(value).strip()


def check_choice(value: Any, field: str, allowed: list[str]) -> str:
    """Проверяет, что значение входит в список допустимых."""
    text = str(value).strip()
    if text not in allowed:
        raise ValidationError(
            f"Поле '{field}' может быть одним из: {', '.join(allowed)}"
        )
    return text


def check_id_list(value: Any, field: str) -> list[int]:
    """Принимает список id или строку вида "1, 2, 3"."""
    if value is None or value == "":
        return []
    if isinstance(value, str):
        value = value.split(",")
    ids = []
    for item in value:
        ids.append(check_id(item, field))
    return ids


# ------------------------------- Классы -------------------------------

class Entity:
    """Базовый класс для всех объектов: у каждого есть id."""

    def __init__(self, id: int) -> None:
        self.id = check_id(id, "id")

    def to_dict(self) -> dict[str, Any]:
        """Возвращает словарь всех полей объекта (для записи в файл)."""
        return dict(self.__dict__)

    def __str__(self) -> str:
        return f"#{self.id}"


class Person(Entity):
    """Человек - общий родитель сотрудника и клиента."""

    def __init__(self, id: int, name: str, email: str) -> None:
        super().__init__(id)
        self.name = check_text(name, "name")
        self.email = check_text(email, "email")
        if "@" not in self.email:
            raise ValidationError("Поле 'email' должно содержать @")

    def __str__(self) -> str:
        return f"#{self.id} {self.name} <{self.email}>"


class Employee(Person):
    """Сотрудник компании."""

    def __init__(self, id: int, name: str, email: str, position: str,
                 department_id: int) -> None:
        super().__init__(id, name, email)
        self.position = check_text(position, "position")
        self.department_id = check_id(department_id, "department_id")

    def __str__(self) -> str:
        return f"{super().__str__()}, {self.position}"


class Client(Person):
    """Клиент (заказчик проекта)."""

    def __init__(self, id: int, name: str, email: str, company: str) -> None:
        super().__init__(id, name, email)
        self.company = check_text(company, "company")

    def __str__(self) -> str:
        return f"{super().__str__()}, компания «{self.company}»"


class Department(Entity):
    """Отдел компании."""

    def __init__(self, id: int, name: str) -> None:
        super().__init__(id)
        self.name = check_text(name, "name")

    def __str__(self) -> str:
        return f"#{self.id} Отдел «{self.name}»"


class Team(Entity):
    """Команда сотрудников."""

    def __init__(self, id: int, name: str, member_ids: list[int]) -> None:
        super().__init__(id)
        self.name = check_text(name, "name")
        self.member_ids = check_id_list(member_ids, "member_ids")

    def __str__(self) -> str:
        return f"#{self.id} Команда «{self.name}», участники {self.member_ids}"


class Project(Entity):
    """Проект, который выполняется для клиента."""

    def __init__(self, id: int, name: str, client_id: int, manager_id: int,
                 start_date: str, deadline: str, status: str,
                 budget: float) -> None:
        super().__init__(id)
        self.name = check_text(name, "name")
        self.client_id = check_id(client_id, "client_id")
        self.manager_id = check_id(manager_id, "manager_id")
        self.start_date = check_date(start_date, "start_date")
        self.deadline = check_date(deadline, "deadline")
        self.status = check_choice(status, "status", PROJECT_STATUSES)
        self.budget = check_number(budget, "budget")
        # даты в формате ГГГГ-ММ-ДД можно сравнивать как строки
        if self.deadline < self.start_date:
            raise ValidationError("Дедлайн не может быть раньше начала")

    def __str__(self) -> str:
        return (f"#{self.id} Проект «{self.name}» [{self.status}], "
                f"{self.start_date} - {self.deadline}")


class Milestone(Entity):
    """Веха (контрольная точка) проекта."""

    def __init__(self, id: int, project_id: int, title: str,
                 due_date: str) -> None:
        super().__init__(id)
        self.project_id = check_id(project_id, "project_id")
        self.title = check_text(title, "title")
        self.due_date = check_date(due_date, "due_date")

    def __str__(self) -> str:
        return f"#{self.id} Веха «{self.title}» до {self.due_date}"


class Task(Entity):
    """Задача внутри проекта."""

    def __init__(self, id: int, project_id: int, title: str,
                 assignee_id: int, priority: str, status: str,
                 estimate_hours: float, due_date: str) -> None:
        super().__init__(id)
        self.project_id = check_id(project_id, "project_id")
        self.title = check_text(title, "title")
        self.assignee_id = check_id(assignee_id, "assignee_id")
        self.priority = check_choice(priority, "priority", PRIORITIES)
        self.status = check_choice(status, "status", TASK_STATUSES)
        self.estimate_hours = check_number(estimate_hours, "estimate_hours")
        self.due_date = check_date(due_date, "due_date")

    def __str__(self) -> str:
        return (f"#{self.id} Задача «{self.title}» [{self.status}, "
                f"{self.priority}], срок {self.due_date}")


class Comment(Entity):
    """Комментарий сотрудника к задаче."""

    def __init__(self, id: int, task_id: int, author_id: int, text: str,
                 created_at: str) -> None:
        super().__init__(id)
        self.task_id = check_id(task_id, "task_id")
        self.author_id = check_id(author_id, "author_id")
        self.text = check_text(text, "text")
        self.created_at = check_date(created_at, "created_at")

    def __str__(self) -> str:
        return f"#{self.id} [{self.created_at}] {self.text}"


class TimeEntry(Entity):
    """Запись о времени, затраченном на задачу."""

    def __init__(self, id: int, task_id: int, employee_id: int,
                 work_date: str, hours: float) -> None:
        super().__init__(id)
        self.task_id = check_id(task_id, "task_id")
        self.employee_id = check_id(employee_id, "employee_id")
        self.work_date = check_date(work_date, "work_date")
        self.hours = check_number(hours, "hours")
        if not 0 < self.hours <= 24:
            raise ValidationError("Часы должны быть от 0 до 24")

    def __str__(self) -> str:
        return f"#{self.id} {self.work_date}: {self.hours} ч"
