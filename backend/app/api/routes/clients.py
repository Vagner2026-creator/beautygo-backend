from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.client import Client
from app.repositories.client_repository import ClientRepository
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter()


@router.post("/", response_model=ClientResponse, status_code=201)
async def create_client_profile(
    data: ClientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = ClientRepository(db)
    if repo.get_by_user_id(current_user.id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Perfil de cliente já existe")
    client = Client(user_id=current_user.id, **data.model_dump())
    return repo.create(client)


@router.get("/me", response_model=ClientResponse)
async def get_my_client_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = ClientRepository(db)
    client = repo.get_by_user_id(current_user.id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado")
    return client


@router.patch("/me", response_model=ClientResponse)
async def update_my_client_profile(
    data: ClientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = ClientRepository(db)
    client = repo.get_by_user_id(current_user.id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(client, field, value)
    return repo.update(client)
