FROM pcraster/emis_base:latest

MAINTAINER Kor de Jong <k.dejong1@uu.nl>

COPY cmd.sh server.py server_flask.py uwsgi.ini /
COPY emis_property /emis_property
COPY test /test

CMD ["/cmd.sh"]
