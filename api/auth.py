from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from api.database import User, get_db

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "").strip().rstrip("/")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "").strip()
AUTH0_ISSUER = f"https://{AUTH0_DOMAIN}/" if AUTH0_DOMAIN else ""
bearer = HTTPBearer(auto_error=False)

@lru_cache(maxsize=1)
def get_jwks() -> dict[str, Any]:
    if not AUTH0_DOMAIN:
        raise RuntimeError("AUTH0_DOMAIN is not configured")
    response = httpx.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json", timeout=10)
    response.raise_for_status()
    return response.json()

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Auth0 token")
    if not AUTH0_DOMAIN or not AUTH0_AUDIENCE:
        raise HTTPException(status_code=500, detail="Auth0 environment variables are not configured")
    try:
        token = credentials.credentials
        header = jwt.get_unverified_header(token)
        key = next(k for k in get_jwks()["keys"] if k["kid"] == header["kid"])
        claims = jwt.decode(token, key, algorithms=["RS256"], audience=AUTH0_AUDIENCE, issuer=AUTH0_ISSUER)
        subject = claims.get("sub")
        email = claims.get("email") or subject
        if not subject:
            raise JWTError("Missing subject")
    except (JWTError, KeyError, StopIteration, RuntimeError, httpx.HTTPError) as exc:
        raise HTTPException(status_code=401, detail="Invalid Auth0 token") from exc

    user = db.query(User).filter(User.auth0_sub == subject).first()
    if not user:
        user = User(auth0_sub=subject, email=email, full_name=claims.get("name") or email, role="user")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
