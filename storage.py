"""Запись данных в файл и чтение из файла в форматах JSON и XML.

Данные передаются словарём:
    {"employees": [{"id": 1, "name": "...", ...}, ...], "tasks": [...], ...}
"""

import json
import xml.etree.ElementTree as ET
from typing import Any

from exceptions import StorageError

Data = dict[str, list[dict[str, Any]]]


class JsonStorage:
    """Хранение данных в формате JSON."""

    def save(self, data: Data, path: str) -> None:
        """Записывает данные в JSON-файл."""
        try:
            with open(path, "w", encoding="utf-8") as file:
                # ensure_ascii=False - русские буквы пишутся как есть
                json.dump(data, file, ensure_ascii=False, indent=4)
        except OSError as error:
            raise StorageError(f"Не удалось записать файл {path}: {error}")

    def load(self, path: str) -> Data:
        """Читает данные из JSON-файла."""
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise StorageError(f"Файл {path} не найден")
        except json.JSONDecodeError as error:
            raise StorageError(f"Файл {path} - некорректный JSON: {error}")
        except (OSError, UnicodeDecodeError) as error:
            raise StorageError(f"Не удалось прочитать файл {path}: {error}")

        # проверяем структуру: объект, в котором каждая коллекция - массив
        if not isinstance(data, dict):
            raise StorageError("В JSON-файле должен быть объект {...}")
        for items in data.values():
            if not isinstance(items, list):
                raise StorageError("Коллекция должна быть массивом [...]")
        return data


class XmlStorage:
    """Хранение данных в формате XML.

    Структура файла:
    <project_management>
        <employees>
            <employee>
                <id>1</id>
                <name>Иван Петров</name>
                ...
            </employee>
        </employees>
        ...
    </project_management>
    """

    # имя тега одного объекта для каждой коллекции
    ITEM_TAGS = {
        "departments": "department",
        "employees": "employee",
        "clients": "client",
        "teams": "team",
        "projects": "project",
        "milestones": "milestone",
        "tasks": "task",
        "comments": "comment",
        "time_entries": "time_entry",
    }

    def save(self, data: Data, path: str) -> None:
        """Записывает данные в XML-файл."""
        root = ET.Element("project_management")
        for name, items in data.items():
            collection = ET.SubElement(root, name)
            for fields in items:
                item = ET.SubElement(collection, self.ITEM_TAGS[name])
                for key, value in fields.items():
                    field = ET.SubElement(item, key)
                    if isinstance(value, list):
                        # список: <member_ids><id>2</id><id>3</id></member_ids>
                        for element in value:
                            ET.SubElement(field, "id").text = str(element)
                    else:
                        field.text = str(value)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ")  # отступы для читаемости
        try:
            tree.write(path, encoding="utf-8", xml_declaration=True)
        except OSError as error:
            raise StorageError(f"Не удалось записать файл {path}: {error}")

    def load(self, path: str) -> Data:
        """Читает данные из XML-файла."""
        try:
            root = ET.parse(path).getroot()
        except FileNotFoundError:
            raise StorageError(f"Файл {path} не найден")
        except ET.ParseError as error:
            raise StorageError(f"Файл {path} - некорректный XML: {error}")
        except OSError as error:
            raise StorageError(f"Не удалось прочитать файл {path}: {error}")

        data: Data = {}
        for collection in root:
            items = []
            for item in collection:
                fields: dict[str, Any] = {}
                for field in item:
                    if len(field) > 0:
                        # есть вложенные теги - это список
                        fields[field.tag] = [child.text for child in field]
                    else:
                        fields[field.tag] = field.text
                items.append(fields)
            data[collection.tag] = items
        return data
