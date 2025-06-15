FROM python:3.11-slim

WORKDIR /app

COPY statistics_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY statistics_service/ ./statistics_service/

CMD ["python", "-m", "statistics_service.app.main"] 