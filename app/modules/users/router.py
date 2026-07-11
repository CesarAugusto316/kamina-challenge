from fastapi import APIRouter, Query, status

from ...core.db_config import InjectedDB
from .schema import UserCreate, UserResponse, UserUpdate
from .service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
def create_user(user_data: UserCreate, db: InjectedDB):
    service = UserService(db)
    return service.create_user(user_data)


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="List all users",
)
def get_all_users(
    db: InjectedDB,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    service = UserService(db)
    return service.get_all_users(skip=skip, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
)
def get_user(user_id: int, db: InjectedDB):
    service = UserService(db)
    return service.get_user(user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
)
def update_user(user_id: int, user_data: UserUpdate, db: InjectedDB):
    service = UserService(db)
    return service.update_user(user_id, user_data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
)
def delete_user(user_id: int, db: InjectedDB):
    service = UserService(db)
    service.delete_user(user_id)
