import logging
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from .router import router
from .config import DATABASE_URL

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Включаем логирование для Kafka
logging.getLogger('kafka').setLevel(logging.INFO)
logging.getLogger('user_service.app.kafka_producer').setLevel(logging.INFO)

app = FastAPI(title="User Service")

register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

app.include_router(router, tags=["users"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)