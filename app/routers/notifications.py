from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse
)
from app import crud

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/",
    response_model=list[NotificationResponse]
)
def get_all_notifications(
    db: Session = Depends(get_db)
):
    return crud.get_all_notifications(db)


@router.get(
    "/researcher/{researcher_id}",
    response_model=list[NotificationResponse]
)
def get_notifications_by_researcher(
    researcher_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_notifications_by_researcher(
        db,
        researcher_id
    )


@router.post(
    "/",
    response_model=NotificationResponse
)
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    return crud.create_notification(
        db,
        notification
    )


@router.put(
    "/{notification_id}",
    response_model=NotificationResponse
)
def update_notification(
    notification_id: int,
    notification: NotificationUpdate,
    db: Session = Depends(get_db)
):

    db_notification = crud.get_notification_by_id(
        db,
        notification_id
    )

    if not db_notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return crud.update_notification(
        db,
        db_notification,
        notification
    )


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):

    db_notification = crud.get_notification_by_id(
        db,
        notification_id
    )

    if not db_notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return crud.delete_notification(
        db,
        db_notification
    )