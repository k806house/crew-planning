FROM python:3.8 as builder

RUN python3.8 -m venv /usr/share/python3/app
ADD requirements.txt /tmp/
RUN pip install --no-cache-dir -Ur /tmp/requirements.txt

FROM builder as server

ADD . /mnt/

WORKDIR /mnt

CMD ["python3", "manage.py"]