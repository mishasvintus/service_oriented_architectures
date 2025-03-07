from fastapi import FastAPI, Request, Response, HTTPException
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="API Gateway")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8001")

ROUTE_MAPPING = {
    "/api/register": "/users/register",
    "/api/login": "/users/login",
    "/api/profile": "/users/profile"
}

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_requests(full_path: str, request: Request):
    mapped_path = ROUTE_MAPPING.get(f"/{full_path}")
    if not mapped_path:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=f"{USER_SERVICE_URL}{mapped_path}",
            headers=dict(request.headers),
            params=request.query_params,
            content=await request.body()
        )

    return Response(content=response.content, status_code=response.status_code, headers=dict(response.headers))
