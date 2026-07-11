from fastapi import HTTPException
from sqlalchemy.orm import Session

from .model import Author
from .schema import AuthorCreate, AuthorUpdate


class AuthorService:
    def __init__(self, db: Session):
        self.db = db

    def create_author(self, author_data: AuthorCreate) -> Author:
        """Crear un nuevo autor"""
        author = Author(**author_data.model_dump())
        self.db.add(author)
        self.db.commit()
        self.db.refresh(author)
        return author

    def get_author(self, author_id: int) -> Author:
        """Obtener un autor por ID"""
        author = self.db.query(Author).filter(Author.id == author_id).first()
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")
        return author

    def get_all_authors(self, skip: int = 0, limit: int = 100) -> list[Author]:
        """Obtener todos los autores con paginación"""
        return self.db.query(Author).offset(skip).limit(limit).all()

    def update_author(self, author_id: int, author_data: AuthorUpdate) -> Author:
        """Actualizar un autor existente"""
        author = self.get_author(author_id)

        update_data = author_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(author, key, value)

        self.db.commit()
        self.db.refresh(author)
        return author

    def delete_author(self, author_id: int) -> dict:
        """Eliminar un autor"""
        author = self.get_author(author_id)

        # Verificar si el autor tiene libros asociados
        if author.books:
            raise HTTPException(
                status_code=400, detail="Cannot delete author with associated books"
            )

        self.db.delete(author)
        self.db.commit()
        return {"message": "Author deleted successfully"}
