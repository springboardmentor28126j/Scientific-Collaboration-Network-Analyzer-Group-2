from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.system_setting import SystemSetting


def list_settings(db: Session) -> list[SystemSetting]:
    return list(db.scalars(select(SystemSetting).order_by(SystemSetting.key)).all())


def get_setting(db: Session, key: str) -> SystemSetting | None:
    return db.scalar(select(SystemSetting).where(SystemSetting.key == key))


def upsert_setting(
    db: Session, key: str, value: str | None, description: str | None, updated_by: int
) -> SystemSetting:
    setting = get_setting(db, key)
    if setting is None:
        setting = SystemSetting(key=key, value=value, description=description, updated_by=updated_by)
        db.add(setting)
    else:
        setting.value = value
        if description is not None:
            setting.description = description
        setting.updated_by = updated_by
    db.commit()
    db.refresh(setting)
    return setting
