from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from gateway.crud.base import CRUDBase
from gateway.models.profile import Profile
from gateway.schemas.profile import ProfileCreate, ProfileUpdate


class CRUDProfile(CRUDBase[Profile, ProfileCreate, ProfileUpdate]):
    def getByEmail(self, db: Session, *, email: str) -> Optional[Profile]:
        return db.query(Profile).filter(Profile.email == email).first()

    def getMultiByEmail(self, db: Session, *, email: str, skip: int = 0, limit: int = 100
                        ) -> List[Profile]:
        return db.query(Profile).filter(Profile.email == email).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: ProfileCreate) -> Profile:
        db_obj = Profile(
            email=obj_in.email,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Profile, obj_in: Union[ProfileUpdate, Dict[str, Any]]
    ) -> Profile:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def delete(self, db: Session, *, id: str) -> None:
        db_obj = db.query(Profile).filter(Profile.id == id).first()
        db.delete(db_obj)
        db.commit()


profile = CRUDProfile(Profile)
