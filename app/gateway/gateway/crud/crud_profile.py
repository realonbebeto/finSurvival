from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from gateway.crud.base import CRUDBase
from gateway.models.profile import Profile
from gateway.schemas.profile import ProfileCreate, ProfileUpdate


class CRUDProfile(CRUDBase[Profile, ProfileCreate, ProfileUpdate]):
    def getByEmail(self, db: Session, *, email: str) -> Optional[Profile]:
        return db.query(Profile).filter(Profile.email == email).first()

    def getMultiByEmail(
        self, db: Session, *, email: str, skip: int = 0, limit: int = 100
    ) -> List[Profile]:
        return (
            db.query(Profile)
            .filter(Profile.email == email)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: ProfileCreate) -> Profile:
        db_obj = Profile(
            age=obj_in.age,
            email=obj_in.email,
            annual_income=obj_in.annual_income,
            monthly_inhand_salary=obj_in.monthly_inhand_salary,
            num_bank_accounts=obj_in.num_bank_accounts,
            num_credit_card=obj_in.num_credit_card,
            interest_rate=obj_in.interest_rate,
            num_of_loan=obj_in.num_of_loan,
            num_of_delayed_payment=obj_in.num_of_delayed_payment,
            changed_credit_limit=obj_in.changed_credit_limit,
            num_credit_inquiries=obj_in.num_credit_inquiries,
            credit_mix=obj_in.credit_mix,
            outstanding_debt=obj_in.outstanding_debt,
            credit_utilization_ratio=obj_in.credit_utilization_ratio,
            credit_history_age=obj_in.credit_history_age,
            payment_of_min_amount=obj_in.payment_of_min_amount,
            total_emi_per_month=obj_in.total_emi_per_month,
            amount_invested_monthly=obj_in.amount_invested_monthly,
            payment_behaviour=obj_in.payment_behaviour,
            monthly_balance=obj_in.monthly_balance,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Profile,
        obj_in: Union[ProfileUpdate, Dict[str, Any]]
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
