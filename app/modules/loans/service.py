from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..books.model import Book
from ..users.model import User
from .model import Loan, LoanStatus
from .schema import LoanCreate, LoanUpdate


class LoanService:
    def __init__(self, db: Session):
        self.db = db

    def create_loan(self, loan_data: LoanCreate) -> Loan:
        """Crear un nuevo préstamo"""
        # Verificar que el usuario existe
        user = self.db.query(User).filter(User.id == loan_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verificar que el libro existe
        book = self.db.query(Book).filter(Book.id == loan_data.book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        # Verificar que el libro no esté prestado actualmente
        active_loan = (
            self.db.query(Loan)
            .filter(Loan.book_id == loan_data.book_id, Loan.status == LoanStatus.ACTIVE)
            .first()
        )
        if active_loan:
            raise HTTPException(status_code=400, detail="Book is already on loan")

        # Calcular fecha esperada de retorno (por defecto 14 días)
        days = loan_data.days if loan_data.days is not None else 14
        expected_return_date = datetime.now(UTC) + timedelta(days=days)

        # FIX: Excluir 'days' del dump porque no es un campo del modelo SQLAlchemy
        loan_data_dict = loan_data.model_dump(exclude={"days"})
        loan = Loan(**loan_data_dict, expected_return_date=expected_return_date)

        self.db.add(loan)
        self.db.commit()
        self.db.refresh(loan)
        return loan

    def get_loan(self, loan_id: int) -> Loan:
        """Obtener un préstamo por ID"""
        loan = self.db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        return loan

    def get_all_loans(self, skip: int = 0, limit: int = 100) -> list[Loan]:
        """Obtener todos los préstamos con paginación"""
        return self.db.query(Loan).offset(skip).limit(limit).all()

    def get_loans_by_user(self, user_id: int) -> list[Loan]:
        """Obtener todos los préstamos de un usuario"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.loans

    def get_loans_by_book(self, book_id: int) -> list[Loan]:
        """Obtener todos los préstamos de un libro"""
        book = self.db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book.loans

    def get_active_loans(self, skip: int = 0, limit: int = 100) -> list[Loan]:
        """Obtener todos los préstamos activos"""
        return (
            self.db.query(Loan)
            .filter(Loan.status == LoanStatus.ACTIVE)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def return_book(self, loan_id: int) -> Loan:
        """Marcar un libro como devuelto"""
        loan = self.get_loan(loan_id)

        if loan.status == LoanStatus.RETURNED:
            raise HTTPException(
                status_code=400, detail="Book has already been returned"
            )

        loan.status = LoanStatus.RETURNED
        loan.actual_return_date = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(loan)
        return loan

    def update_loan(self, loan_id: int, loan_data: LoanUpdate) -> Loan:
        """Actualizar un préstamo existente"""
        loan = self.get_loan(loan_id)

        update_data = loan_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(loan, key, value)

        self.db.commit()
        self.db.refresh(loan)
        return loan

    def delete_loan(self, loan_id: int):
        """Eliminar un préstamo"""
        loan = self.get_loan(loan_id)

        if loan.status == LoanStatus.ACTIVE:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete active loan. Return the book first.",
            )

        self.db.delete(loan)
        self.db.commit()
        return
