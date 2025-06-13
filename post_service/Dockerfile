FROM python:3.11-slim

WORKDIR /app

COPY post_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "post_service.app.main"] 