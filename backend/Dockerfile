FROM python:3.12-slim
 # Requirements for `psycorg2` and script "/app/run_app.sh".
 # RUN apt-get update &&\
 #     apt-get upgrade -y &&\
 # It also create directory `/app`.
 WORKDIR /app
 COPY requirements.txt ./
 RUN apt-get update \
     && apt-get upgrade -y\
     && apt-get -y install libpq-dev gcc \
     && pip install psycopg2
 RUN pip install -U pip &&\
     pip install -r requirements.txt --no-cache-dir
 COPY . .
 # RUN python manage.py makemigrations
 # RUN python manage.py migrate;
 # RUN python manage.py collectstatic --noinput;
 CMD ["gunicorn", "-w", "2", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]