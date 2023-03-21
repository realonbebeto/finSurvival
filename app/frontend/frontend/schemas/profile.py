from typing import Optional, List

from pydantic import BaseModel, EmailStr


class ProfileModel(BaseModel):
    age: float
    annual_income: float
    monthly_inhand_salary: float
    num_bank_accounts: float
    num_credit_card: float
    interest_rate: float
    num_of_loan: float
    num_of_delayed_payment: float
    changed_credit_limit: float
    num_credit_inquiries: float
    credit_mix: str
    outstanding_debt: float
    credit_utilization_ratio: float
    credit_history_age: float
    payment_of_min_amount: str
    total_emi_per_month: float
    amount_invested_monthly: float
    payment_behaviour: str
    monthly_balance: float


class ProfileBase(BaseModel):
    age: float
    email: Optional[EmailStr]
    annual_income: float
    monthly_inhand_salary: float
    num_bank_accounts: float
    num_credit_card: float
    interest_rate: float
    num_of_loan: float
    num_of_delayed_payment: float
    changed_credit_limit: float
    num_credit_inquiries: float
    credit_mix: str
    outstanding_debt: float
    credit_utilization_ratio: float
    credit_history_age: float
    payment_of_min_amount: float
    total_emi_per_month: float
    amount_invested_monthly: float
    payment_behaviour: str
    monthly_balance: float


class ProfileCreate(ProfileBase):
    pass


# Properties to receive via API on update
class ProfileUpdate(ProfileBase):
    times: Optional[List[int]]
    hazard_score: Optional[List[int]]
    risk_score: Optional[List[int]]
    survival_score: Optional[List[int]]


class ProfileInDBBase(ProfileBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class ProfileReport(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    times: Optional[List[int]]
    hazard_score: Optional[List[int]]
    risk_score: Optional[List[int]]
    survival_score: Optional[List[int]]

    class Config:
        orm_mode = True


class Profile(ProfileInDBBase):
    pass
