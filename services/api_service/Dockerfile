FROM python:3.11-slim 
WORKDIR /app
COPY services/api_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/api_service/ ./api_service/ 

CMD ["uvicorn", "api_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]