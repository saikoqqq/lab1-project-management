# ЛР №1. Вариант 24 — «Управление проектами»

ООП в Python, обработка исключений, хранение данных в XML и JSON.

## Запуск

```bash
python main.py
```

При запуске программа загружает данные из `data/data.json`. Через меню можно
просматривать, добавлять, изменять и удалять объекты (CRUD), а также
сохранять и загружать данные в форматах JSON и XML.

## Структура проекта

| Файл | Содержимое |
|---|---|
| `models.py` | 11 классов предметной области и функции проверки значений |
| `exceptions.py` | собственные исключения |
| `service.py` | `ProjectManagementSystem` — хранение объектов и CRUD |
| `storage.py` | `JsonStorage`, `XmlStorage` — запись и чтение файлов |
| `main.py` | `ConsoleApp` — консольное меню |
| `diagram.drawio` | UML-диаграмма классов (draw.io, 3 листа) |
| `data/data.json`, `data/data.xml` | пример данных в обоих форматах |
| `docs/` | отчёт о лабораторной работе и листы диаграммы в PNG |

## Классы предметной области

- `Entity` — базовый класс: поле `id`, метод `to_dict()`;
- `Person` → `Employee` (сотрудник), `Client` (заказчик);
- `Department` — отдел;
- `Team` — команда сотрудников;
- `Project` — проект;
- `Milestone` — веха проекта;
- `Task` — задача;
- `Comment` — комментарий к задаче;
- `TimeEntry` — затраченное на задачу время.

Объект создаётся из словаря: `Employee(**data)`. Все значения проверяются
в конструкторе.

## Исключения

Собственные (`exceptions.py`), все наследуются от `AppError`:

| Исключение | Когда возникает |
|---|---|
| `ValidationError` | пустое поле, email без @, неверная дата или число, неизвестный статус |
| `NotFoundError` | объекта с таким id нет |
| `StorageError` | файл не найден, повреждённый JSON/XML, ошибка в данных файла |

Встроенные исключения, которые обрабатываются: `ValueError`, `TypeError`,
`FileNotFoundError`, `OSError`, `json.JSONDecodeError`,
`xml.etree.ElementTree.ParseError`, `UnicodeDecodeError`, `KeyboardInterrupt`,
`EOFError`. В главном цикле меню ошибки перехватываются, поэтому программа
не завершается при неправильном вводе.

## Структура JSON

```json
{
    "departments": [{"id": 1, "name": "Разработка"}],
    "employees": [
        {"id": 1, "name": "Иван Петров", "email": "petrov@company.ru",
         "position": "Менеджер проектов", "department_id": 1}
    ],
    "teams": [{"id": 1, "name": "Backend", "member_ids": [2, 3]}],
    "tasks": [
        {"id": 1, "project_id": 1, "title": "Спроектировать БД",
         "assignee_id": 2, "priority": "high", "status": "done",
         "estimate_hours": 8.0, "due_date": "2026-09-15"}
    ]
}
```

Остальные коллекции (`clients`, `projects`, `milestones`, `comments`,
`time_entries`) устроены так же.

## Структура XML

```xml
<?xml version='1.0' encoding='utf-8'?>
<project_management>
    <employees>
        <employee>
            <id>1</id>
            <name>Иван Петров</name>
            <email>petrov@company.ru</email>
            <position>Менеджер проектов</position>
            <department_id>1</department_id>
        </employee>
    </employees>
    <teams>
        <team>
            <id>1</id>
            <name>Backend</name>
            <member_ids>
                <id>2</id>
                <id>3</id>
            </member_ids>
        </team>
    </teams>
</project_management>
```
