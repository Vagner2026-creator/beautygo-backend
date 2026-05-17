from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_professional
from app.models.user import User
from app.schemas.media import MediaResponse
from app.services.media_service import MediaService

router = APIRouter()


@router.get("/professionals/{professional_id}/media", response_model=List[MediaResponse])
async def list_media(professional_id: int, db: Session = Depends(get_db)):
    return MediaService(db).list_media(professional_id)


@router.post("/upload", response_model=MediaResponse, status_code=201)
async def upload_media(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_professional),
    db: Session = Depends(get_db),
):
    return await MediaService(db).save_upload(current_user, file, description)


@router.delete("/{media_id}", status_code=204)
async def delete_media(
    media_id: int,
    current_user: User = Depends(get_current_professional),
    db: Session = Depends(get_db),
):
    MediaService(db).delete_media(current_user, media_id)
