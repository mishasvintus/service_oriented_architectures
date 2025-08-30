from fastapi import APIRouter, Request, Response, HTTPException
from httpx import AsyncClient
import os
from dotenv import load_dotenv

from ..auth import get_current_user_id
from fastapi import Depends
import httpx

load_dotenv()

router = APIRouter()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8001")

@router.api_route("/api/register", methods=["POST"])
@router.api_route("/api/login", methods=["POST"])
@router.api_route("/api/profile", methods=["GET", "PUT", "DELETE"])
async def proxy_to_user_service(request: Request):
    path = request.url.path.replace('/api', '/users', 1)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=f"{USER_SERVICE_URL}{path}",
                headers={k: v for k, v in request.headers.items() if k.lower() != 'host'},
                params=request.query_params,
                content=await request.body(),
                timeout=5.0
            )
            return Response(content=response.content, status_code=response.status_code, headers=response.headers)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {e}") 