from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from sqlalchemy.orm import Session

from app.core.db_config import InjectedDB

from ...core.vars import JWT_ALGORITHM, JWT_SECRET
from .model import User
from .schema import (
    JWTPayload,
    JWTRequest,
    JWTResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)

InjectedAuthCredentials = Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]
password_hasher = PasswordHash((Argon2Hasher(),))


class UserService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def check_valid_credentials(
        request: Request, credentials: InjectedAuthCredentials, db: InjectedDB
    ) -> User:
        """
        Check if the provided credentials are valid and return the corresponding user.
        """
        try:
            raw_payload = jwt.decode(
                credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM]
            )
            if raw_payload is None:
                raise HTTPException(status_code=401, detail="Payload is empty")

            jwt_payload = JWTPayload(**raw_payload)
            service = UserService(db)
            user = service.get_user(int(jwt_payload.sub))  # jwt_payload.sub=user.id
            request.state.user = user
            return user

        except (jwt.ExpiredSignatureError, InvalidTokenError):
            raise HTTPException(status_code=401, detail="JWT Expired or Invalid")

    # private method
    def _encode_jwt(
        self, subject: str | int, expires_delta: timedelta = timedelta(hours=3)
    ) -> str:
        """
        Create a JWT token for the given subject and expiration delta.
        """
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Crear un nuevo usuario"""
        # Verificar si el email ya existe
        existing_user = (
            self.db.query(User).filter(User.email == user_data.email).first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = password_hasher.hash(user_data.password)
        user = User(
            name=user_data.name, email=user_data.email, password_hash=hashed_password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return UserResponse(
            id=user.id, name=user.name, email=user.email, created_at=user.created_at
        )

    def login_user(self, credentials: JWTRequest) -> JWTResponse:
        user = self.db.query(User).filter(User.email == credentials.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        is_valid = password_hasher.verify(credentials.password, user.password_hash)

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        jwt = self._encode_jwt(user.id)
        return JWTResponse(access_token=jwt)

    def get_user(self, user_id: int) -> User:
        """Obtener un usuario por ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_user_by_email(self, email: str) -> User:
        """Obtener un usuario por email"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Obtener todos los usuarios con paginación"""
        return self.db.query(User).offset(skip).limit(limit).all()

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Actualizar un usuario existente"""
        user = self.get_user(user_id)

        update_data = user_data.model_dump(exclude_unset=True)

        # Verificar si el nuevo email ya existe
        if "email" in update_data:
            existing_user = (
                self.db.query(User)
                .filter(User.email == update_data["email"], User.id != user_id)
                .first()
            )
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")

        for key, value in update_data.items():
            setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> dict:
        """Eliminar un usuario"""
        user = self.get_user(user_id)
        self.db.delete(user)
        self.db.commit()
        return {"message": "User deleted successfully"}
