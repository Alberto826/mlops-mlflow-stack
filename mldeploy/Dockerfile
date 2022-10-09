FROM python:3.7-slim-buster

COPY ./app/requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ./app .

ENTRYPOINT flask run --host=0.0.0.0
