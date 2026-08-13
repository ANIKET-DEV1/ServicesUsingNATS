import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from ..config import get_config
from ..schemas.user import UserCreate, UserLogin

router = APIRouter()
settings = get_config()


def _client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


async def _proxy(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    *,
    json_body: dict | None = None,
    params: dict | None = None,
    headers: dict | None = None,
) -> JSONResponse:
    url = f"{settings.USER_SERVICE_URL}{path}"

    forward_headers = {
        k: v
        for k, v in (headers or {}).items()
        if k.lower() in ("authorization", "accept")
    }

    try:
        resp = await client.request(
            method,
            url,
            json=json_body,
            params=params,
            headers=forward_headers,
            timeout=10.0,
        )
    except httpx.ConnectError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="User Service is unreachable.")
    except httpx.TimeoutException:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="User Service did not respond in time.")

    return JSONResponse(content=resp.json(), status_code=resp.status_code)


@router.post("/register", tags=["Users"])
async def register(cred: UserCreate, request: Request, client: httpx.AsyncClient = Depends(_client)):
    return await _proxy(
        client, "POST", "/users/register",
        json_body={
            "username": cred.username,
            "email": cred.email,
            "password": cred.password.get_secret_value(),
            "confirm_password": cred.confirm_password.get_secret_value(),
        },
        headers=dict(request.headers),
    )


@router.post("/login", tags=["Users"])
async def login(cred: UserLogin, request: Request, client: httpx.AsyncClient = Depends(_client)):
    return await _proxy(
        client, "POST", "/users/login",
        json_body={
            "username": cred.username,
            "password": cred.password.get_secret_value(),
        },
        headers=dict(request.headers),
    )


@router.get("/me", tags=["Users"])
async def get_me(request: Request, client: httpx.AsyncClient = Depends(_client)):
    return await _proxy(client, "GET", "/users/me", headers=dict(request.headers))


@router.get("/verify-email", tags=["Users"])
async def verify_email(
    request: Request,
    token: str = Query(..., description="Email verification token"),
    client: httpx.AsyncClient = Depends(_client),
):
    return await _proxy(client, "GET", "/users/verify-email", params={"token": token}, headers=dict(request.headers))
