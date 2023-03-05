from sqlalchemy import Column, Integer, String
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy_utils import EmailType

from gateway.db.base_class import Base


class Profile(Base):

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(EmailType, nullable=False, unique=True)
    # other attributes
    score = Column()
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        server_default=text("now()"), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True),
                        onupdate=datetime.now(timezone.utc))
