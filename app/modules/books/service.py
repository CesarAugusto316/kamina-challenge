from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from ..authors.model import Author
from .model import Book
from .schema import BookCreate, BookUpdate


class BookService:
    def __init__(self, db: Session):
        self.db = db

    def create_book(self, book_data: BookCreate) -> Book:
        """Crear un nuevo libro"""
        # Verificar que el autor existe
        author = self.db.query(Author).filter(Author.id == book_data.author_id).first()
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")

        book = Book(**book_data.model_dump())
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def get_book(self, book_id: int) -> Book:
        """Obtener un libro por ID"""
        book = self.db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book

    def get_all_books(self, skip: int = 0, limit: int = 100) -> list[Book]:
        """Obtener todos los libros con paginación"""
        return self.db.query(Book).offset(skip).limit(limit).all()

    def search_books(
        self,
        title: str | None = None,
        author_name: str | None = None,
        year: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Book]:
        """Buscar libros por título, nombre de autor o año"""
        query = self.db.query(Book).options(joinedload(Book.author))

        if title:
            query = query.filter(Book.title.ilike(f"%{title}%"))

        if author_name:
            query = query.join(Author).filter(Author.name.ilike(f"%{author_name}%"))

        if year:
            query = query.filter(Book.publication_year == year)

        return query.offset(skip).limit(limit).all()

    def update_book(self, book_id: int, book_data: BookUpdate) -> Book:
        """Actualizar un libro existente"""
        book = self.get_book(book_id)

        update_data = book_data.model_dump(exclude_unset=True)

        # Verificar que el nuevo autor existe si se proporciona
        if "author_id" in update_data:
            author = (
                self.db.query(Author)
                .filter(Author.id == update_data["author_id"])
                .first()
            )
            if not author:
                raise HTTPException(status_code=404, detail="Author not found")

        for key, value in update_data.items():
            setattr(book, key, value)

        self.db.commit()
        self.db.refresh(book)
        return book

    def delete_book(self, book_id: int) -> dict:
        """Eliminar un libro"""
        book = self.get_book(book_id)

        # Verificar si el libro tiene préstamos activos
        active_loans = [loan for loan in book.loans if loan.status.value == "active"]
        if active_loans:
            raise HTTPException(
                status_code=400, detail="Cannot delete book with active loans"
            )

        self.db.delete(book)
        self.db.commit()
        return {"message": "Book deleted successfully"}
