from fastapi import APIRouter, Query, status

from ...core.db_config import InjectedDB
from .schema import BookCreate, BookResponse, BookUpdate
from .service import BookService

router = APIRouter(prefix="/books", tags=["Books"])


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
)
def create_book(book_data: BookCreate, db: InjectedDB):
    service = BookService(db)
    return service.create_book(book_data)


@router.get(
    "/",
    response_model=list[BookResponse],
    summary="List or search books",
    description=(
        "List all books. Optionally filter by title, author name, or publication year. "
        "When any filter is provided, it behaves as a search endpoint."
    ),
)
def get_books(
    db: InjectedDB,
    title: str | None = Query(None, description="Filter by title (partial match)"),
    author_name: str | None = Query(
        None, description="Filter by author name (partial match)"
    ),
    year: int | None = Query(None, description="Filter by exact publication year"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    service = BookService(db)

    # Si hay algún filtro, comportarse como búsqueda
    if title or author_name or year:
        return service.search_books(
            title=title,
            author_name=author_name,
            year=year,
            skip=skip,
            limit=limit,
        )

    return service.get_all_books(skip=skip, limit=limit)


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Get a book by ID",
)
def get_book(book_id: int, db: InjectedDB):
    service = BookService(db)
    return service.get_book(book_id)


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    summary="Update a book",
)
def update_book(book_id: int, book_data: BookUpdate, db: InjectedDB):
    service = BookService(db)
    return service.update_book(book_id, book_data)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a book",
)
def delete_book(book_id: int, db: InjectedDB):
    service = BookService(db)
    service.delete_book(book_id)
