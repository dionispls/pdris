## Разворачивание проекта

#### Docker-compose
1) Создайте виртуальное окружение и активируйте его.
2) Создайте файл .env 
```commandline
# Database settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Django settings
SITE_DOMAIN=localhost:8000
SECRET_KEY=django-insecure-your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Static files
STATIC_URL=/static/
STATIC_ROOT=/app/static/

# Media files
MEDIA_URL=/media/
MEDIA_ROOT=/app/media/
```
3) Перейдите в папку `infra` и выполните сборку контейнеров:
    ```sh
    docker-compose up -d --build
    ```
4) Приложение будет запущено на localhost