FROM python:3.14-slim-trixie

RUN pip install gunicorn
RUN apt update && apt install -y adb && rm -rf /var/lib/apt/lists/*
RUN mkdir /android && ln -s /android /root/.android

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /src
COPY . /src

ENTRYPOINT [ "/usr/local/bin/gunicorn", "-w", "1", "-b", "0.0.0.0", "app:app"]