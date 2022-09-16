FROM python:3.7-slim-buster

COPY ./app .

RUN pip install -r requirements.txt

ENTRYPOINT flask run --host=0.0.0.0
