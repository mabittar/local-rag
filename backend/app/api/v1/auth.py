from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.auth import Token, UserLogin
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(
        credentials.username, credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token_for_user(user)
    return Token(access_token=access_token)


@router.post("/logout")
async def logout(
    response: Response,
) -> dict:
    """Logout endpoint - in JWT stateless mode this is mainly client-side."""
    return {"message": "Logout successful"}
