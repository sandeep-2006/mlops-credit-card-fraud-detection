FROM python:3.10-slim
WORKDIR /app

# install deps
COPY services/fraud-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy source
COPY services/fraud-service/src /app

# create models directory and copy trained model and scaler from repo
RUN mkdir -p /app/models
COPY training/models/logistic.joblib /app/models/logistic.joblib
COPY training/processed/amount_scaler.joblib /app/models/amount_scaler.joblib

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8080", "-w", "1"]
