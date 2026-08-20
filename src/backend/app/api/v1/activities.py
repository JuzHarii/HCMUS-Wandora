from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...api.deps import get_current_user, get_db
from ...models.activity_interaction import ActivityComment, ActivityVote
from ...models.itinerary import ItineraryActivity
from ...models.user import User
from ...schemas.activity_interaction import CommentCreate, CommentResponse, VoteCreate, VoteResponse

router = APIRouter()


@router.post("/{activity_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    activity_id: int,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CommentResponse:
    """UC 2.15: Gửi bình luận cho 1 Hoạt động (Activity)."""
    activity = db.query(ItineraryActivity).filter(ItineraryActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Activity with id {activity_id} not found")

    new_comment = ActivityComment(
        activity_id=activity_id,
        user_id=current_user.id,
        content=comment_in.content,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return CommentResponse(
        id=new_comment.id,
        activity_id=new_comment.activity_id,
        user_id=new_comment.user_id,
        user_name=current_user.full_name or current_user.email,
        content=new_comment.content,
        created_at=new_comment.created_at,
    )


@router.get("/{activity_id}/comments", response_model=list[CommentResponse])
def get_comments(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CommentResponse]:
    """UC 2.15: Lấy danh sách bình luận của 1 Hoạt động (Activity)."""
    activity = db.query(ItineraryActivity).filter(ItineraryActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Activity with id {activity_id} not found")

    comments = db.query(ActivityComment).filter(ActivityComment.activity_id == activity_id).order_by(ActivityComment.created_at.asc()).all()

    result = []
    for comment in comments:
        user_name = comment.user.full_name or comment.user.email if comment.user else None
        result.append(
            CommentResponse(
                id=comment.id,
                activity_id=comment.activity_id,
                user_id=comment.user_id,
                user_name=user_name,
                content=comment.content,
                created_at=comment.created_at,
            )
        )
    return result


@router.post("/{activity_id}/vote", response_model=VoteResponse)
def vote_activity(
    activity_id: int,
    vote_in: VoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActivityVote:
    """UC 2.15: Bình chọn Hoạt động (Upsert nếu user đã bình chọn trước đó)."""
    activity = db.query(ItineraryActivity).filter(ItineraryActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Activity with id {activity_id} not found")

    if vote_in.vote_value not in (1, -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vote_value. Allowed values are 1 (Upvote) or -1 (Downvote)",
        )

    existing_vote = (
        db.query(ActivityVote)
        .filter(ActivityVote.activity_id == activity_id, ActivityVote.user_id == current_user.id)
        .first()
    )

    if existing_vote:
        existing_vote.vote_value = vote_in.vote_value
        db.commit()
        db.refresh(existing_vote)
        return existing_vote

    new_vote = ActivityVote(
        activity_id=activity_id,
        user_id=current_user.id,
        vote_value=vote_in.vote_value,
    )
    db.add(new_vote)
    db.commit()
    db.refresh(new_vote)
    return new_vote
