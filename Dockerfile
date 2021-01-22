FROM python:3

ENV PYTHONUNBUFFERED=1
ENV APP_ENV=PRD
ENV APP_VERSION=1.0.0
ENV SECRET_KEY=""
ENV ALLOWED_HOST=""
ENV DB_NAME=db
ENV DB_USER=mono
ENV DB_PASS=

WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r requirements.txt

COPY ./mono /code/

# RUN ["chmod", "+x", "./entrypoint.sh"]

EXPOSE 8000

# CMD ["/bin/bash", "./entrypoint.sh"]