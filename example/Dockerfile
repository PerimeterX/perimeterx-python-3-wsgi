FROM debian:buster

RUN apt update && apt install -y python3-pip
RUN pip3 install gunicorn
RUN pip3 install Django
RUN pip3 install perimeterx-python-3-wsgi

WORKDIR /tmp/px
CMD ["/tmp/px/scripts/run_gunicorn.sh"]
