import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from os import getenv
import aiofiles
from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from sqlalchemy import select

from database.database import AsyncSession, get_db
from models.models import Media, User

STATUS_CREATED = 201
STATUS_NOT_FOUND = 404
CONTENT_TYPE_ERROR = 415

load_dotenv()
router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/medias", status_code=STATUS_CREATED)
async def upload_media(
    file: UploadFile = File(..., description="Файл изображения"),
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Подставляет картинки"""
    stmt = select(User).where(User.api_key == api_key)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=STATUS_NOT_FOUND, detail="User not found")
    content_type = file.content_type.lower()
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=CONTENT_TYPE_ERROR, detail="Only images allowed"
        )

    file_uuid = uuid.uuid4().hex
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    file_path = UPLOAD_DIR / f"{file_uuid}.{file_ext}"

    content = await file.read()
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    media = Media(
        filename=file.filename, filepath=str(file_path), created_at=datetime.now()
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)

    return {
        "result": True,
        "media_id": media.id,
    }
