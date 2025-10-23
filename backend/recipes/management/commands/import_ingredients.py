from recipes.models import Ingredient
from .base_import import BaseImportCommand


class Command(BaseImportCommand):
    help = 'Импортирует продукты из файла'
    file_path = 'data/ingredients.json'
    model = Ingredient
