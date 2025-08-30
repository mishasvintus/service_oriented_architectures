from fastapi import FastAPI
from .routers import posts_router, user_proxy_router, statistics_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="API Gateway")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(statistics_router.router)
app.include_router(posts_router.router)
app.include_router(user_proxy_router.router)
