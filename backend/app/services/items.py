from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from app.schemas.item import Item, ItemCreate, ItemUpdate


class ItemsService:
    """In-memory example service.

    Replace with database persistence as needed.
    """

    def __init__(self) -> None:
        self._items: Dict[int, Item] = {}
        self._counter: int = 0

    async def list_items(self) -> List[Item]:
        return list(self._items.values())

    async def create_item(self, payload: ItemCreate) -> Item:
        self._counter += 1
        item = Item(id=self._counter, name=payload.name, description=payload.description, created_at=datetime.utcnow())
        self._items[item.id] = item
        return item

    async def get_item(self, item_id: int) -> Optional[Item]:
        return self._items.get(item_id)

    async def update_item(self, item_id: int, payload: ItemUpdate) -> Optional[Item]:
        existing = self._items.get(item_id)
        if not existing:
            return None
        updated = existing.copy(update=payload.dict(exclude_unset=True))
        self._items[item_id] = updated
        return updated

    async def delete_item(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None
