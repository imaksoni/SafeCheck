from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from firebase_admin import auth
from app.db.session import get_db
from app.models.user import User

router = APIRouter()

class TokenPayload(BaseModel):
    token: str

class UserResponse(BaseModel):
    id: int
    firebase_uid: str
    email: str | None = None
    phone: str | None = None
    full_name: str | None = None

    class Config:
        from_attributes = True

@router.post("/firebase-login", response_model=UserResponse)
def firebase_login(payload: TokenPayload, db: Session = Depends(get_db)):
    try:
        decoded_token = auth.verify_id_token(payload.token)
        firebase_uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        phone = decoded_token.get("phone_number")

        # In Firebase, name can be in token claims depending on auth provider
        full_name = decoded_token.get("name")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase ID token",
        )

    if not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()

    if not user:
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            phone=phone,
            full_name=full_name,
        )
        db.add(user)
    else:
        # Update user info if changed from Firebase
        if email and user.email != email:
            user.email = email
        if phone and user.phone != phone:
            user.phone = phone
        if full_name and user.full_name != full_name:
            user.full_name = full_name

    db.commit()
    db.refresh(user)

    return user
