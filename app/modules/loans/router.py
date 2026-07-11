from fastapi import APIRouter, Depends, Query, status

from ...core.db_config import InjectedDB
from ..users.service import UserService
from .schema import LoanCreate, LoanResponse, LoanUpdate
from .service import LoanService

router = APIRouter(
    prefix="/loans",
    tags=["Loans"],
    # makes all routes private
    dependencies=[Depends(UserService.check_valid_credentials)],
)


# -------------------------------------------
# PRIVATE ROUTES
# -------------------------------------------
@router.post(
    "/",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new loan",
)
def create_loan(loan_data: LoanCreate, db: InjectedDB):
    service = LoanService(db)
    return service.create_loan(loan_data)


@router.get(
    "/",
    response_model=list[LoanResponse],
    summary="List all loans",
    status_code=status.HTTP_200_OK,
)
def get_all_loans(
    db: InjectedDB,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    service = LoanService(db)
    return service.get_all_loans(skip=skip, limit=limit)


@router.get(
    "/active",
    response_model=list[LoanResponse],
    summary="List all active loans",
    status_code=status.HTTP_200_OK,
)
def get_active_loans(
    db: InjectedDB,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    service = LoanService(db)
    return service.get_active_loans(skip=skip, limit=limit)


@router.get(
    "/user/{user_id}",
    response_model=list[LoanResponse],
    summary="Get all loans for a specific user",
    status_code=status.HTTP_200_OK,
)
def get_loans_by_user(user_id: int, db: InjectedDB):
    service = LoanService(db)
    return service.get_loans_by_user(user_id)


@router.get(
    "/book/{book_id}",
    response_model=list[LoanResponse],
    summary="Get all loans for a specific book",
    status_code=status.HTTP_200_OK,
)
def get_loans_by_book(book_id: int, db: InjectedDB):
    service = LoanService(db)
    return service.get_loans_by_book(book_id)


@router.get(
    "/{loan_id}",
    response_model=LoanResponse,
    summary="Get a loan by ID",
    status_code=status.HTTP_200_OK,
)
def get_loan(loan_id: int, db: InjectedDB):
    service = LoanService(db)
    return service.get_loan(loan_id)


@router.put(
    "/{loan_id}/return",
    response_model=LoanResponse,
    summary="Return a book",
    description="Mark a loan as returned and set the actual return date.",
    status_code=status.HTTP_200_OK,
)
def return_book(loan_id: int, db: InjectedDB):
    service = LoanService(db)
    return service.return_book(loan_id)


@router.put(
    "/{loan_id}",
    response_model=LoanResponse,
    summary="Update a loan",
    status_code=status.HTTP_200_OK,
)
def update_loan(loan_id: int, loan_data: LoanUpdate, db: InjectedDB):
    service = LoanService(db)
    return service.update_loan(loan_id, loan_data)


@router.delete(
    "/{loan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a loan",
)
def delete_loan(loan_id: int, db: InjectedDB):
    service = LoanService(db)
    return service.delete_loan(loan_id)
