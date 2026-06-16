FROM python:3.10-slim
WORKDIR /app

# install deps
COPY services/transaction-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy source
COPY services/transaction-service/src /app

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8080", "-w", "1"]
