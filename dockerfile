FROM python:3.7-slim


WORKDIR /api_yamdb/app

COPY /api_yamdb/requirements.txt /app

RUN pip3 install -r /api_yamdb/app/requirements.txt --no-cache-dir

COPY ./ /app



CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ]