FROM python:3.8

WORKDIR /usr/src/app

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt \

RUN mkdir -p volumes/mysql/data

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]