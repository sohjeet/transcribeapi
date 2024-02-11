from typing import Optional
from pydantic import BaseModel,field_validator
from datetime import datetime
from app import settings
from users.schemas import UserInDB

'''Audio Conversion Schemas'''
# class AudioConversionCreate(BaseModel):
#     audio_file: UploadFile = File(None)

class AudioConversionResponse(BaseModel):
    id: int
    text_content: str
    user: UserInDB
    created_at: Optional[datetime]
    
    @field_validator("created_at", mode="before")
    def default_datetime(cls, value: datetime) -> datetime:
        return value or datetime.now()

    class Config:
        orm_mode = True