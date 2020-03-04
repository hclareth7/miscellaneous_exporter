FROM python:3.6-slim

RUN mkdir -p /usr/src/app/metrics
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt

COPY metrics/* /usr/src/app/metrics/
COPY miscellaneous_exporter.py /usr/src/app

EXPOSE 9797
ENV VIRTUAL_PORT=9797 DEBUG=0 SUPPORTED_LANG=python,bash

ENTRYPOINT [ "python", "-u", "./miscellaneous_exporter.py" ]
CMD []