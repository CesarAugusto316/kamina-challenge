from fastapi import APIRouter, Query, status

from ...core.db_config import InjectedDB
from .schema import AuthorCreate, AuthorResponse, AuthorUpdate
from .service import AuthorService

router = APIRouter(prefix="/authors", tags=["Authors"])


@router.post(
    "/",
    response_model=AuthorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new author",
)
def create_author(author_data: AuthorCreate, db: InjectedDB):
    service = AuthorService(db)
    return service.create_author(author_data)


@router.get(
    "/",
    response_model=list[AuthorResponse],
    summary="List all authors",
)
def get_all_authors(
    db: InjectedDB,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    service = AuthorService(db)
    return service.get_all_authors(skip=skip, limit=limit)


@router.get(
    "/{author_id}",
    response_model=AuthorResponse,
    summary="Get an author by ID",
)
def get_author(author_id: int, db: InjectedDB):
    service = AuthorService(db)
    return service.get_author(author_id)


@router.put(
    "/{author_id}",
    response_model=AuthorResponse,
    summary="Update an author",
)
def update_author(author_id: int, author_data: AuthorUpdate, db: InjectedDB):
    service = AuthorService(db)
    return service.update_author(author_id, author_data)


@router.delete(
    "/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an author",
)
def delete_author(author_id: int, db: InjectedDB):
    service = AuthorService(db)
    service.delete_author(author_id)
