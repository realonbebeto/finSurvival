from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy_utils import EmailType

from gateway.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    full_name = Column(String, index=True)
    email = Column(EmailType, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=datetime.now(timezone.utc))
