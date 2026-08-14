"""Persistence operations for a workspace packing checklist."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.packing import PackingItem
from app.schemas.packing import PackingItemCreate, PackingItemUpdate


class PackingService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_items(self, workspace_id: str) -> list[PackingItem]:
        return self.db.scalars(
            select(PackingItem)
            .where(PackingItem.workspace_id == workspace_id)
            .order_by(PackingItem.is_completed, PackingItem.created_at.desc())
        ).all()

    def create_item(self, workspace_id: str, payload: PackingItemCreate) -> PackingItem:
        item = PackingItem(workspace_id=workspace_id, **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_item(self, item_id: str, payload: PackingItemUpdate) -> PackingItem:
        item = self.db.get(PackingItem, item_id)
        if item is None:
            raise ValueError("Packing item does not exist.")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        self.db.commit()
        self.db.refresh(item)
        return item
