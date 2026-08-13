import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse

from ..config import get_config

router = APIRouter()
settings = get_config()

#helper

def _client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


async def _proxy(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    *,
    body: bytes | None = None,
    params: dict | None = None,
    headers: dict | None = None,
) -> JSONResponse:
    url = f"{settings.USER_SERVICE_URL}{path}"

    forward_headers = {
        k: v
        for k, v in (headers or {}).items()
        if k.lower() in ("authorization", "content-type", "accept")
    }

    try:
        resp = await client.request(
            method,
            url,
            content=body,
            params=params,
            headers=forward_headers,
            timeout=10.0,
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User Service is unreachable.",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="User Service did not respond in time.",
        )

    return JSONResponse(
        content=resp.json(),
        status_code=resp.status_code,
    )



@router.post(
    "/register",
    tags=["Users"],
)
async def register(request: Request, client: httpx.AsyncClient = Depends(_client)):
    body = await request.body()
    return await _proxy(client, "POST", "/users/register", body=body, headers=dict(request.headers))


@router.post(
    "/login",
    tags=["Users"],
)
async def login(request: Request, client: httpx.AsyncClient = Depends(_client)):
    body = await request.body()
    return await _proxy(client, "POST", "/users/login", body=body, headers=dict(request.headers))


@router.get(
    "/me",
    tags=["Users"],
)
async def get_me(request: Request, client: httpx.AsyncClient = Depends(_client)):
    return await _proxy(client, "GET", "/users/me", headers=dict(request.headers))


@router.get(
    "/verify-email",
 tags=["Users"],
)
async def verify_email(
    request: Request,
    token: str = Query(..., description="Email verification token"),
    client: httpx.AsyncClient = Depends(_client),
):
    return await _proxy(
        client, "GET", "/users/verify-email",
        params={"token": token},
        headers=dict(request.headers),
    )
