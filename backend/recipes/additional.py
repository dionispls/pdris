"""Настройки параметров."""
from enum import Enum, IntEnum


class Tuples(tuple, Enum):
    """Кортежи с предопределёнными параметрами."""
    RECIPE_IMAGE_SIZE = 500, 500
    SYMBOL_TRUE_SEARCH = "1", "true"
    SYMBOL_FALSE_SEARCH = "0", "false"


class Limits(IntEnum):
    """Ограничения для различных полей и параметров приложения."""
    MAX_LEN_EMAIL_FIELD = 256
    MAX_LEN_USERS_CHARFIELD = 32
    MAX_LEN_RECIPES_CHARFIELD = 64
    MAX_LEN_MEASUREMENT = 256
    MIN_COOKING_TIME = 1
    MIN_AMOUNT_INGREDIENTS = 1
    MAX_MEASUREMENT = 64
