from datetime import datetime, timezone

from sqlalchemy import ARRAY, Column, Float, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy_utils import EmailType

from gateway.db.base_class import Base


class Profile(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(EmailType, nullable=False, unique=False)
    age = Column(Integer, nullable=False, unique=False)
    annual_income = Column(Float, nullable=False, unique=False)
    monthly_inhand_salary = Column(Float, nullable=False, unique=False)
    num_bank_accounts = Column(Float, nullable=False, unique=False)
    num_credit_card = Column(Float, nullable=False, unique=False)
    interest_rate = Column(Float, nullable=False, unique=False)
    num_of_loan = Column(Float, nullable=False, unique=False)
    num_of_delayed_payment = Column(Float, nullable=False, unique=False)
    changed_credit_limit = Column(Float, nullable=False, unique=False)
    num_credit_inquiries = Column(Float, nullable=False, unique=False)
    credit_mix = Column(String, nullable=False, unique=False)
    outstanding_debt = Column(Float, nullable=False, unique=False)
    credit_utilization_ratio = Column(Float, nullable=False, unique=False)
    credit_history_age = Column(Float, nullable=False, unique=False)
    payment_of_min_amount = Column(String, nullable=False, unique=False)
    total_emi_per_month = Column(Float, nullable=False, unique=False)
    amount_invested_monthly = Column(Float, nullable=False, unique=False)
    payment_behaviour = Column(String, nullable=False, unique=False)
    monthly_balance = Column(Float, nullable=False, unique=False)
    # other attributes
    times = Column(ARRAY(Float), nullable=True, unique=False)
    hazard_score = Column(ARRAY(Float), nullable=True, unique=False)
    risk_score = Column(ARRAY(Float), nullable=True, unique=False)
    survival_score = Column(ARRAY(Float), nullable=True, unique=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(TIMESTAMP(timezone=True),
                        onupdate=datetime.now(timezone.utc))
