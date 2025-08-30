FROM python:3.11-slim

WORKDIR /app

COPY services/post_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/post_service/ ./post_service/

CMD ["python", "-m", "post_service.app.main"] 