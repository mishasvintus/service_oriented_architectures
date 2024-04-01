FROM python:3.11-slim  
WORKDIR /user_service
ENV PYTHONPATH=/user_service
COPY user_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY user_service/. .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
