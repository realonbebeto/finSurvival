# Import all the models, so that Base has them before being
# imported by Alembic
from auth.db.base_class import Base
from auth.models.user import User
from auth.models.profile import Profile
