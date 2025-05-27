from backend.core.database import Base, engine
from backend.core import models  # Ensure models are imported

Base.metadata.create_all(bind=engine)
print("Tables created.")
