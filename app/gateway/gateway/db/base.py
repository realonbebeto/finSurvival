# Import all the models, so that Base has them before being
# imported by Alembic
from gateway.db.base_class import Base
from gateway.models.profile import Profile
from gateway.models.user import User
