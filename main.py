"""Консольное приложение «Управление проектами».

Запуск: python main.py
"""

import os

from exceptions import AppError, ValidationError
from service import ProjectManagementSystem
from storage import JsonStorage, XmlStorage

# Папка data рядом с этим файлом: __file__ - путь к main.py,
# поэтому файлы находятся, из какой бы папки ни запустили программу
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
JSON_FILE = os.path.join(DATA_DIR, "data.json")
XML_FILE = os.path.join(DATA_DIR, "data.xml")

# Названия коллекций для меню
TITLES: dict[str, str] = {
    "departments": "Отделы",
    "employees": "Сотрудники",
    "clients": "Клиенты",
    "teams": "Команды",
    "projects": "Проекты",
    "milestones": "Вехи",
    "tasks": "Задачи",
    "comments": "Комментарии",
    "time_entries": "Учёт времени",
}

# Поля, которые пользователь вводит при создании объекта: (поле, подсказка)
FIELDS: dict[str, list[tuple[str, str]]] = {
    "departments": [("name", "Название")],
    "employees": [("name", "Имя"), ("email", "Email"),
                  ("position", "Должность"), ("department_id", "id отдела")],
    "clients": [("name", "Имя"), ("email", "Email"),
                ("company", "Компания")],
    "teams": [("name", "Название"),
              ("member_ids", "id участников через запятую")],
    "projects": [("name", "Название"), ("client_id", "id клиента"),
                 ("manager_id", "id менеджера"),
                 ("start_date", "Дата начала ГГГГ-ММ-ДД"),
                 ("deadline", "Дедлайн ГГГГ-ММ-ДД"),
                 ("status", "Статус (planned/active/completed)"),
                 ("budget", "Бюджет")],
    "milestones": [("project_id", "id проекта"), ("title", "Название"),
                   ("due_date", "Срок ГГГГ-ММ-ДД")],
    "tasks": [("project_id", "id проекта"), ("title", "Название"),
              ("assignee_id", "id исполнителя"),
              ("priority", "Приоритет (low/medium/high)"),
              ("status", "Статус (todo/in_progress/done)"),
              ("estimate_hours", "Оценка, ч"),
              ("due_date", "Срок ГГГГ-ММ-ДД")],
    "comments": [("task_id", "id задачи"), ("author_id", "id автора"),
                 ("text", "Текст"), ("created_at", "Дата ГГГГ-ММ-ДД")],
    "time_entries": [("task_id", "id задачи"),
                     ("employee_id", "id сотрудника"),
                     ("work_date", "Дата ГГГГ-ММ-ДД"), ("hours", "Часы")],
}


class ConsoleApp:
    """Текстовое меню для работы с системой."""

    def __init__(self, system: ProjectManagementSystem) -> None:
        self.system = system

    def run(self) -> None:
        """Главный цикл программы."""
        while True:
            print("\n===== Управление проектами =====")
            print("1. Показать все  2. Показать один  3. Добавить")
            print("4. Изменить      5. Удалить")
            print("6. Сохранить в JSON  7. Загрузить из JSON")
            print("8. Сохранить в XML   9. Загрузить из XML")
            print("0. Выход")
            choice = input("Выберите пункт: ").strip()
            if choice == "0":
                break
            # все ошибки обрабатываются здесь, программа не завершается
            try:
                self.do_action(choice)
            except AppError as error:
                print(f"Ошибка: {error}")
            except ValueError:
                print("Ошибка: нужно ввести целое число")

    def do_action(self, choice: str) -> None:
        """Выполняет пункт меню с номером choice."""
        if choice == "1":
            self.show_all()
        elif choice == "2":
            self.show_one()
        elif choice == "3":
            self.create()
        elif choice == "4":
            self.update()
        elif choice == "5":
            self.delete()
        elif choice == "6":
            self.save(JsonStorage(), JSON_FILE)
        elif choice == "7":
            self.load(JsonStorage(), JSON_FILE)
        elif choice == "8":
            self.save(XmlStorage(), XML_FILE)
        elif choice == "9":
            self.load(XmlStorage(), XML_FILE)
        else:
            print("Нет такого пункта меню")

    def choose_collection(self) -> str:
        """Спрашивает у пользователя коллекцию и возвращает её имя."""
        names = list(TITLES)
        number = 1
        for name in names:
            print(f"{number}. {TITLES[name]}")
            number += 1
        number = int(input("Номер коллекции: "))
        if not 1 <= number <= len(names):
            raise ValidationError("Нет коллекции с таким номером")
        return names[number - 1]

    def show_all(self) -> None:
        """Выводит все объекты выбранной коллекции."""
        name = self.choose_collection()
        entities = self.system.read_all(name)
        if not entities:
            print("Список пуст")
        for entity in entities:
            print(entity)

    def show_one(self) -> None:
        """Выводит все поля одного объекта."""
        name = self.choose_collection()
        entity = self.system.read(name, int(input("id: ")))
        for field, value in entity.to_dict().items():
            print(f"  {field}: {value}")

    def create(self) -> None:
        """Запрашивает поля и добавляет новый объект."""
        name = self.choose_collection()
        fields = {}
        for field, prompt in FIELDS[name]:
            fields[field] = input(f"{prompt}: ")
        print(f"Добавлено: {self.system.create(name, fields)}")

    def update(self) -> None:
        """Изменяет одно поле объекта."""
        name = self.choose_collection()
        entity_id = int(input("id: "))
        fields = self.system.read(name, entity_id).to_dict()
        print(f"Поля: {', '.join(fields)}")
        field = input("Какое поле изменить: ").strip()
        value = input("Новое значение: ")
        entity = self.system.update(name, entity_id, field, value)
        print(f"Изменено: {entity}")

    def delete(self) -> None:
        """Удаляет объект по id."""
        name = self.choose_collection()
        print(f"Удалено: {self.system.delete(name, int(input('id: ')))}")

    def save(self, storage: JsonStorage | XmlStorage, path: str) -> None:
        """Сохраняет все данные в файл (JSON или XML)."""
        storage.save(self.system.to_data(), path)
        print(f"Сохранено в {path}")

    def load(self, storage: JsonStorage | XmlStorage, path: str) -> None:
        """Загружает все данные из файла (JSON или XML)."""
        self.system.load_data(storage.load(path))
        print(f"Загружено из {path}")


def main() -> None:
    """Точка входа: загрузка данных и запуск меню."""
    system = ProjectManagementSystem()
    try:
        system.load_data(JsonStorage().load(JSON_FILE))
        print(f"Загружены данные из {JSON_FILE}")
    except AppError as error:
        print(f"Данные не загружены ({error}), начинаем с пустой базы")

    try:
        ConsoleApp(system).run()
    except (KeyboardInterrupt, EOFError):
        print("\nПрограмма завершена")


if __name__ == "__main__":
    main()
