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

#### Kubernetes

1) Собери Docker образы:
```bash
cd backend
docker build -t foodgram-backend:latest .

cd ../frontend
docker build -t foodgram-frontend:latest .
```

2) Примени манифесты Kubernetes:
```bash
kubectl apply -f k8s/
```

Или по отдельности:
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap-nginx.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/nginx.yaml
kubectl apply -f k8s/ingress.yaml
```

3) Проверь статус подов:
```bash
kubectl get pods -n foodgram
```

4) Выполни миграции Django:
```bash
POD=$(kubectl get pod -n foodgram -l app=foodgram-backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD -n foodgram -- python manage.py migrate
kubectl exec -it $POD -n foodgram -- python manage.py collectstatic --noinput
```

5) Открой приложение:
```bash
kubectl port-forward -n foodgram svc/foodgram-nginx 8080:80
```
Открой http://localhost:8080

Или получи внешний IP:
```bash
kubectl get svc foodgram-nginx -n foodgram
```

Полезные команды:
- Логи: `kubectl logs -f deployment/foodgram-backend -n foodgram`
- Удалить все: `kubectl delete -f k8s/`