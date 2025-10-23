from recipes.models import Tag
from .base_import import BaseImportCommand


class Command(BaseImportCommand):
    help = 'Импортирует теги из файла'
    file_path = 'data/tags.json'
    model = Tag
