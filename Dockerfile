FROM python:3.10-alpine

RUN pip install --upgrade pip

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./api /app

WORKDIR /app

COPY ./script/entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]
