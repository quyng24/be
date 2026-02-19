from fastapi import APIRouter, HTTPException, Response, status
from firebase_admin import auth

from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.auth import TokenRequest

router = APIRouter(tags=["Auth"])


@router.post("/login")
async def login(data: TokenRequest, response: Response) -> dict:
    try:
        decoded = auth.verify_id_token(data.token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token",
        ) from exc

    email = str(decoded.get("email", "")).strip().lower()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in Firebase token",
        )

    allowed_emails = {item.lower() for item in settings.ALLOWED_EMAILS}
    if email not in allowed_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    session_token = create_access_token({"sub": email})
    response.set_cookie(
        key="session",
        value=session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.SESSION_EXPIRE_MINUTES * 60,
    )

    name = str(decoded.get("name", "")).strip() or email

    return {
        "message": "Login success",
        "status": 200,
        "user": {
            "name": name,
            "email": email,
        },
    }

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="session",
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return {
        "status": 2000,
        "message": "Logged out"
    }