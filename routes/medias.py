from datetime import datetime

import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from models.database import AsyncSession, get_db
from schemas.medias_schema import  MediasResponse
from models.db_orm import Media

router = APIRouter()
UPLOAD_DIR = Path('./uploads')

@router.post("/medias", response_model= MediasResponse)
async def upload_media(
    file: UploadFile = File(..., description="Файл изображения"),
    api_key: str = Header(..., alias='api-key'),
    db: AsyncSession = Depends(get_db)
):
    if api_key != "your-secret-key":
        raise HTTPException(status_code=401, detail="Unauthorized")


    media = Media(
        filename=file.filename,
        filepath=f"uploads/{file.filename}",
        size=len(await file.read())
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)

    return MediasResponse(result=True, media_id=media.id)




