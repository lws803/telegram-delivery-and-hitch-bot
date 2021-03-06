FROM python:3

ADD service.py /
ADD cleanup_service.py /
ADD common /common
ADD matcher /matcher
ADD helpers /helpers
ADD requirements.txt /

RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install -y supervisor

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]
