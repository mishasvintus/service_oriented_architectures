from fastapi import FastAPI
from user_service.app.dependencies import init_db
from user_service.app.routers import users_router

app = FastAPI(title="User Service")

init_db(app)
app.include_router(users_router.router, tags=["users"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)