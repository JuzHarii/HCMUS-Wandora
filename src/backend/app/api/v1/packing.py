"""Endpoints for the shared packing list available after a trip is saved."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_workspace_member
from app.db.session import get_db
from app.models.packing import PackingItem
from app.models.user import User
from app.schemas.packing import PackingItemCreate, PackingItemResponse, PackingItemUpdate
from app.services.packing_service import PackingService
from app.services.workspace_service import WorkspaceService


router = APIRouter(tags=["packing"])


@router.get("/workspaces/{workspace_id}/packing-items", response_model=list[PackingItemResponse])
def list_packing_items(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PackingItem]:
    require_workspace_member(db, workspace_id, current_user.id)
    WorkspaceService(db).get_workspace(workspace_id)
    return PackingService(db).list_items(workspace_id)


@router.post("/workspaces/{workspace_id}/packing-items", response_model=PackingItemResponse, status_code=status.HTTP_201_CREATED)
def create_packing_item(
    workspace_id: str,
    payload: PackingItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PackingItem:
    require_workspace_member(db, workspace_id, current_user.id)
    WorkspaceService(db).get_workspace(workspace_id)
    return PackingService(db).create_item(workspace_id, payload)


@router.patch("/packing-items/{item_id}", response_model=PackingItemResponse)
def update_packing_item(
    item_id: str,
    payload: PackingItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PackingItem:
    item = db.get(PackingItem, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Packing item does not exist.")
    require_workspace_member(db, item.workspace_id, current_user.id)
    return PackingService(db).update_item(item_id, payload)
