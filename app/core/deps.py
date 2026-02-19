from fastapi import HTTPException, Request, status

from app.core.security import verify_session_token


def get_current_user(request: Request) -> str:
    token = request.cookies.get("session")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = verify_session_token(token)
        email = payload.get("sub") or payload.get("email")
        if not isinstance(email, str) or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session payload",
            )
        return email
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )
