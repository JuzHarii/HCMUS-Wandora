from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.packing import PackingAssignmentRequest, PackingItemCreate, PackingItemResponse, PackingItemUpdate, PackingSuggestionResult
from app.services import packing_service

router = APIRouter()


@router.post("/workspaces/{workspace_id}/packing/suggestions", response_model=PackingSuggestionResult)
async def generate_packing_suggestions(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PackingSuggestionResult:
    """Sinh danh sách gợi ý hành lý bằng AI cho chuyến đi."""
    items_list, is_fallback = await packing_service.generate_packing_suggestions(db, workspace_id)
    return PackingSuggestionResult(
        items=[PackingItemResponse.model_validate(item) for item in items_list],
        is_fallback=is_fallback
    )


@router.get("/workspaces/{workspace_id}/packing", response_model=list[PackingItemResponse])
async def list_packing_items(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PackingItemResponse]:
    """Lấy danh sách đồ dùng hành lý của workspace."""
    res = packing_service.list_packing_items(db, workspace_id)
    return [PackingItemResponse.model_validate(item) for item in res]


@router.post(
    "/workspaces/{workspace_id}/packing", response_model=PackingItemResponse, status_code=status.HTTP_201_CREATED
)
async def add_packing_item(
    workspace_id: str,
    payload: PackingItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PackingItemResponse:
    """Thêm đồ dùng mới vào danh sách hành lý."""
    res = packing_service.add_packing_item(db, workspace_id, payload)
    return PackingItemResponse.model_validate(res)


@router.put("/packing/items/{item_id}", response_model=PackingItemResponse)
async def update_packing_item(
    item_id: str,
    payload: PackingItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PackingItemResponse:
    """Cập nhật thông tin đồ dùng hành lý."""
    res = packing_service.update_packing_item(db, item_id, payload)
    return PackingItemResponse.model_validate(res)


@router.post("/packing/items/{item_id}/assign", response_model=PackingItemResponse)
async def assign_or_toggle_item(
    item_id: str,
    payload: PackingAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PackingItemResponse:
    """Phân công vật dụng cho thành viên hoặc cập nhật cờ hoàn thành (is_checked)."""
    res = packing_service.assign_or_toggle_item(
        db, item_id=item_id, user_id=payload.user_id, is_checked=payload.is_checked
    )
    return PackingItemResponse.model_validate(res)


@router.delete("/packing/items/{item_id}")
async def delete_packing_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Xóa vật dụng khỏi danh sách hành lý."""
    return packing_service.delete_packing_item(db, item_id)
