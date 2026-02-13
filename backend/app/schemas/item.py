from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(..., example="Flashcards")
    description: Optional[str] = Field(None, example="AI-assisted flashcards for job interview prep")


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    name: Optional[str] = Field(None, example="Updated flashcards name")


class Item(ItemBase):
    id: int = Field(..., example=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
