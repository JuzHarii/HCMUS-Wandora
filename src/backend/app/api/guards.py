from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .deps import get_db
from ..models.workspace import Workspace


def check_trip_is_planned(workspace_id: int, db: Session = Depends(get_db)) -> Workspace:
    """Dependency kiểm tra Workspace đã ở trạng thái Planned chưa. Trả lỗi 403 nếu đang là Draft."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with id {workspace_id} not found",
        )

    if workspace.status.lower() == "draft":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Trip is currently in Draft status. Please save and plan itinerary first.",
        )

    return workspace
