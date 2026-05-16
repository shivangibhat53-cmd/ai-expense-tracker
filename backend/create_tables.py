from app.db.session import get_engine
from app.db.base import Base
from app.models import user

engine = get_engine()

Base.metadata.create_all(bind=engine)

print("Tables created successfully")