# mdTeXerPad
#
# VERSION               0.1

FROM debian:buster-slim
#FROM ubuntu:19.10

# install stuff
RUN apt-get update && apt-get install -y python3 python3-websockets python3-markdown gunicorn3

# copy stuff to the container
RUN mkdir /mtp
WORKDIR /mtp
COPY ./ ./
RUN groupadd -r mtp && useradd --no-log-init -r -g mtp mtp
RUN chown mtp:mtp * -R
USER mtp

EXPOSE 8081
EXPOSE 8082
CMD    ["python3", "mdTeXerPad.py"]
# for n cores use 2n+1 workers
#CMD gunicorn3 -w $(expr $(nproc) \* 2 + 1) -b :8081 mdTeXerPad:app
