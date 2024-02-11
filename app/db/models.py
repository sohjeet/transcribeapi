from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    current_credit = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

class AudioConversion(Base):
    __tablename__ = "audio_conversions"

    id = Column(Integer, primary_key=True, index=True)
    # audio_file_path = Column(String, index=True, unique=True)
    text_content = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="audio_conversions")
    
# Add a back_populates relationship in the User model
User.audio_conversions = relationship("AudioConversion", back_populates="user", cascade="all, delete-orphan")
