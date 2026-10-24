"""Система управления проектами: хранит все объекты и выполняет CRUD."""

from typing import Any

from exceptions import NotFoundError, StorageError, ValidationError
from models import (Client, Comment, Department, Employee, Entity,
                    Milestone, Project, Task, Team, TimeEntry)

# Коллекции программы: имя коллекции -> класс её объектов
CLASSES: dict[str, type[Entity]] = {
    "departments": Department,
    "employees": Employee,
    "clients": Client,
    "teams": Team,
    "projects": Project,
    "milestones": Milestone,
    "tasks": Task,
    "comments": Comment,
    "time_entries": TimeEntry,
}


class ProjectManagementSystem:
    """Хранит объекты всех коллекций и выполняет операции CRUD."""

    def __init__(self) -> None:
        # для каждой коллекции - словарь {id: объект}
        self.data: dict[str, dict[int, Entity]] = {
            name: {} for name in CLASSES
        }

    def get_collection(self, name: str) -> dict[int, Entity]:
        """Возвращает словарь объектов коллекции по её имени."""
        if name not in self.data:
            raise ValidationError(f"Неизвестная коллекция '{name}'")
        return self.data[name]

    @staticmethod
    def build(name: str, fields: dict[str, Any]) -> Entity:
        """Создаёт объект класса коллекции name из словаря полей."""
        try:
            return CLASSES[name](**fields)
        except TypeError:
            # не хватает полей, есть лишние поля или fields - не словарь
            raise ValidationError(f"Неверный набор полей для '{name}'")

    # ------------------------------ CRUD ------------------------------

    def create(self, name: str, fields: dict[str, Any]) -> Entity:
        """Create: создаёт объект, id назначается автоматически."""
        items = self.get_collection(name)
        new_id = max(items, default=0) + 1
        entity = self.build(name, {"id": new_id, **fields})
        items[new_id] = entity
        return entity

    def read(self, name: str, entity_id: int) -> Entity:
        """Read: возвращает объект по id."""
        items = self.get_collection(name)
        if entity_id not in items:
            raise NotFoundError(f"В коллекции '{name}' нет объекта "
                                f"с id={entity_id}")
        return items[entity_id]

    def read_all(self, name: str) -> list[Entity]:
        """Read: возвращает все объекты коллекции."""
        return list(self.get_collection(name).values())

    def update(self, name: str, entity_id: int, field: str,
               value: Any) -> Entity:
        """Update: меняет одно поле объекта.

        Объект создаётся заново из словаря, поэтому новое значение
        проверяется так же, как при создании.
        """
        fields = self.read(name, entity_id).to_dict()
        if field == "id" or field not in fields:
            raise ValidationError(f"Поле '{field}' нельзя изменить")
        fields[field] = value
        entity = self.build(name, fields)
        self.get_collection(name)[entity_id] = entity
        return entity

    def delete(self, name: str, entity_id: int) -> Entity:
        """Delete: удаляет объект по id и возвращает его."""
        entity = self.read(name, entity_id)
        del self.get_collection(name)[entity_id]
        return entity

    # ------------------------ Работа с файлами ------------------------

    def to_data(self) -> dict[str, list[dict[str, Any]]]:
        """Преобразует все объекты в словари для записи в файл."""
        return {name: [entity.to_dict() for entity in items.values()]
                for name, items in self.data.items()}

    def load_data(self, data: dict[str, list[dict[str, Any]]]) -> None:
        """Заменяет все объекты данными, прочитанными из файла.

        Если в данных есть ошибка, старые данные остаются без изменений.
        """
        new_data: dict[str, dict[int, Entity]] = {name: {} for name in CLASSES}
        try:
            for name, items in data.items():
                if name not in CLASSES:
                    raise ValidationError(f"Неизвестная коллекция '{name}'")
                for fields in items:
                    entity = self.build(name, fields)
                    new_data[name][entity.id] = entity
        except ValidationError as error:
            raise StorageError(f"Ошибка в данных файла: {error}")
        self.data = new_data
