FROM pcraster/emis_base:latest

MAINTAINER Kor de Jong <k.dejong1@uu.nl>

# COPY requirements.txt /
# RUN pip install -r requirements.txt

COPY cmd.sh server.py server_flask.py server_wsgi.py uwsgi.ini /
COPY property /property
COPY test /test

CMD ["/cmd.sh"]
