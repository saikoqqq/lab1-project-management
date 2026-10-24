"""Собственные исключения программы «Управление проектами»."""


class AppError(Exception):
    """Базовое исключение программы. От него наследуются остальные."""


class ValidationError(AppError):
    """Некорректное значение поля (пустое имя, неверная дата и т.п.)."""


class NotFoundError(AppError):
    """Объект с указанным id не найден."""


class StorageError(AppError):
    """Ошибка чтения или записи файла JSON / XML."""
