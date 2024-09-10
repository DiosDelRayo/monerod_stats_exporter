FROM python:3.12-slim

WORKDIR /app

COPY monerod_stats_exporter.py /app/
COPY docker-compose-config.yml /app/config.yml

RUN pip install prometheus-client requests pyyaml

VOLUME [ "/data", "/app" ]
EXPOSE 9123

CMD ["python", "-u", "monerod_stats_exporter.py"]

