# pull the official base image
FROM python:3.13

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update && apt-get install -y postgresql-client

RUN pip install --upgrade pip

COPY ./requirements.txt /app/
RUN pip install -r requirements.txt --no-cache-dir
RUN touch /var/container_initialized

# copy project
COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver","0.0.0.0:8000"]
