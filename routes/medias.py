import uuid
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os
import aiofiles
from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile

from models.database import AsyncSession, get_db
from models.db_orm import Media
from schemas.medias_schema import MediasResponse

load_dotenv()
router = APIRouter()
UPLOAD_DIR = Path("./uploads")
SECRET_KEY=os.getenv("SECRET_KEY")

@router.post("/medias", response_model=MediasResponse)
async def upload_media(
    file: UploadFile = File(..., description="Файл изображения"),
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_db),
):
    if api_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    media = Media(
        filename=file.filename,
        filepath=f"uploads/{file.filename}",
        size=len(await file.read()),
        created_at=datetime.now(),
        content_type=file.content_type,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)

    return MediasResponse(result=True, media_id=media.id)
