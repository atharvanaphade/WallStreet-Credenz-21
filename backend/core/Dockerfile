FROM python:3.9.5

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip3 install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

COPY . /usr/src/app/

RUN ["chmod", "+x", "/usr/src/app/entrypoint.sh"]

ENTRYPOINT ["sh", "/usr/src/app/entrypoint.sh"]
