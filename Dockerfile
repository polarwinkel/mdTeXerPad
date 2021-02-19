# mdTeXerPad
#
# VERSION               0.1

FROM debian:bullseye-slim
#FROM ubuntu:19.10

# install stuff
RUN apt-get update && apt-get install -y \
    python3 \
    python3-websockets \
    python3-markdown \
    gunicorn3 \
    python3-flask \
    python3-flask-sockets

# copy stuff to the container
RUN mkdir /mtp
WORKDIR /mtp
COPY ./ ./
RUN groupadd -r mtp && useradd --no-log-init -r -g mtp mtp
RUN chown mtp:mtp * -R
#USER mtp

EXPOSE 8000
#CMD    ["python3", "app.py"]
CMD gunicorn3 -k flask_sockets.worker --bind 0.0.0.0:8000 -w 1 --timeout 3600 --keep-alive 10 --error-logfile /var/log/gunicorn/error.log --access-logfile /var/log/gunicorn/access.log app:app
#CMD gunicorn3 -k flask_sockets.worker --bind 0.0.0.0:8000 -w 1 --timeout 3600 --keep-alive 10 app:app
