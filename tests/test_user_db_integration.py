import uuid

from sqlalchemy import text

from app.database import SessionLocal, engine
from app import models


def _db_is_available() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

def test_create_and_read_user_from_real_db():
    if not _db_is_available():
        return

    db = SessionLocal()
    new_id = uuid.uuid4()
    email = f"integration_{new_id}@example.com"

    try:
        user = models.User(
            user_id=new_id,
            username="integration_user",
            email=email,
            password_hash="test_hash",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        fetched = (
            db.query(models.User)
            .filter(models.User.user_id == new_id)
            .first()
        )

        assert fetched is not None
        assert fetched.username == "integration_user"
        assert fetched.email == email

    finally:
        # На всякий случай откатываем текущую транзакцию
        try:
            db.rollback()
        except Exception:
            pass

        # Пытаемся удалить созданного пользователя (если он есть)
        try:
            db.query(models.User).filter(models.User.user_id == new_id).delete()
            db.commit()
        except Exception:
            pass
        finally:
            db.close()
