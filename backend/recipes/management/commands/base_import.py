import json
from pathlib import Path

from django.core.management.base import BaseCommand


class BaseImportCommand(BaseCommand):
    """Базовая команда для импорта данных из JSON."""

    file_path = None
    model = None

    def handle(self, *args, **options):
        if not self.file_path or not self.model:
            self.stdout.write(self.style.ERROR(
                "file_path и model должны быть заданы."
            ))
            return

        file = Path(self.file_path)
        try:
            with file.open('r', encoding='utf-8') as f:
                data = json.load(f)

            created = self.model.objects.bulk_create(
                (self.model(**item) for item in data),
                ignore_conflicts=True
            )

            self.stdout.write(self.style.SUCCESS(
                f'Импортировано {len(created)} новых объектов '
                f'в {self.model.__name__} из файла {file.name}.'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при импорте из файла "{file.name}": {e}'
            ))
