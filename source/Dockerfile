FROM python:3.5

MAINTAINER Kor de Jong <k.dejong1@uu.nl>

COPY requirements.txt /
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN groupadd -r uwsgi && useradd -r -g uwsgi uwsgi

COPY cmd.sh server.py server_flask.py server_wsgi.py uwsgi.ini /
COPY property /property
COPY test /test

USER uwsgi
CMD ["/cmd.sh"]
