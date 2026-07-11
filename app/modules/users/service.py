from fastapi import HTTPException
from sqlalchemy.orm import Session

from .model import User
from .schema import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        """Crear un nuevo usuario"""
        # Verificar si el email ya existe
        existing_user = (
            self.db.query(User).filter(User.email == user_data.email).first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(**user_data.model_dump())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

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
