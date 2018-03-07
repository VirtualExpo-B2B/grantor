FROM python:3-alpine3.7

RUN pip install PyMySQL && mkdir /usr/src/perms

COPY . /usr/src/grantor
WORKDIR /usr/src/grantor

VOLUME /usr/src/perms
ENTRYPOINT [ "./grantor.py", "-P", "../perms" ]
