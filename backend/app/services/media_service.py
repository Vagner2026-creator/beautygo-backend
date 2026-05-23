import os
import uuid
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status
from app.models.professional_media import ProfessionalMedia, MediaType
from app.models.user import User
from app.repositories.media_repository import MediaRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.schemas.media import MediaResponse

ALLOWED_PHOTO_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov"}
MAX_PHOTO_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB


class MediaService:
    def __init__(self, db: Session):
        self.repo = MediaRepository(db)
        self.pro_repo = ProfessionalRepository(db)

    def _get_professional_for_user(self, user: User):
        professional = self.pro_repo.get_by_user_id(user.id)
        if not professional:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil profissional não encontrado",
            )
        return professional

    def list_media(self, professional_id: int) -> List[MediaResponse]:
        media_list = self.repo.list_by_professional(professional_id)
        return [MediaResponse.model_validate(m) for m in media_list]

    async def save_upload(
        self, user: User, file: UploadFile, description: str = None
    ) -> MediaResponse:
        professional = self._get_professional_for_user(user)

        filename = file.filename or ""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

        if ext in ALLOWED_PHOTO_EXTENSIONS:
            media_type = MediaType.PHOTO
            max_size = MAX_PHOTO_SIZE
        elif ext in ALLOWED_VIDEO_EXTENSIONS:
            media_type = MediaType.VIDEO
            max_size = MAX_VIDEO_SIZE
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extensão '{ext}' não permitida. Fotos: jpg, jpeg, png, webp. Vídeos: mp4, mov.",
            )

        contents = await file.read()
        if len(contents) > max_size:
            limit_mb = max_size // (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Arquivo muito grande. Limite: {limit_mb} MB.",
            )

        upload_dir = os.path.join("uploads", str(professional.id))
        os.makedirs(upload_dir, exist_ok=True)

        unique_filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(upload_dir, unique_filename)

        with open(file_path, "wb") as f:
            f.write(contents)

        file_url = f"/uploads/{professional.id}/{unique_filename}"

        media = ProfessionalMedia(
            professional_id=professional.id,
            type=media_type,
            file_url=file_url,
            thumbnail_url=None,
            description=description,
        )
        created = self.repo.create(media)
        return MediaResponse.model_validate(created)

    def delete_media(self, user: User, media_id: int) -> None:
        professional = self._get_professional_for_user(user)

        media = self.repo.get_by_id(media_id)
        if not media:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mídia não encontrada")
        if media.professional_id != professional.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

        # Try to remove file from disk
        if media.file_url:
            relative_path = media.file_url.lstrip("/")
            if not relative_path.startswith("uploads/"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Caminho de arquivo inválido",
                )
            if os.path.exists(relative_path):
                try:
                    os.remove(relative_path)
                except OSError:
                    pass

        self.repo.delete(media)
