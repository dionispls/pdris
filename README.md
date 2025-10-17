## Разворачивание проекта

#### Docker-compose
1) Создайте виртуальное окружение и активируйте его.
2) Сгенерируйте SECRET_KEY для Django:
3) Перейдите в папку `infra` и выполните сборку контейнеров:
    ```sh
    docker-compose up -d --build
    ```
5) Создайте и настройте базу данных:
    ```sh
    docker-compose exec backend python manage.py migrate
    docker-compose exec backend python manage.py createsuperuser
    docker-compose exec backend python manage.py collectstatic --no-input
    ```