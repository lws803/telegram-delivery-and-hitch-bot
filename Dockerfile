FROM python:3

ADD service.py /
ADD common /common
ADD matcher /matcher
ADD helpers /helpers
ADD requirements.txt /

RUN pip install -r requirements.txt

CMD python service.py
