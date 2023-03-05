from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from gateway.crud.base import CRUDBase
from gateway.models.user import User
from gateway.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def getByEmail(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def isActive(self, user: User) -> bool:
        return user.is_active

    def isSuperuser(self, user: User) -> bool:
        return user.is_superuser

    def delete(self, db: Session, *, email: str) -> None:
        db_obj = db.query(User).filter(User.email == email).first()
        db.delete(db_obj)
        db.commit()


user = CRUDUser(User)
