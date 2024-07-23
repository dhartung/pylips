FROM python:3.8.3-slim-buster

WORKDIR /src
COPY . /src

RUN pip install -r ./requirements.txt
RUN pip install gunicorn


ENTRYPOINT [ "/usr/local/bin/gunicorn", "-w", "1", "-b", "0.0.0.0", "app:app"]