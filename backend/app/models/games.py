from sqlalchemy import Column, Integer, String, UUID
from .database import Base
import uuid

class Game(Base):
    __tablename__ = "games"
    
    game_id = Column(String(16), primary_key=True, default=lambda: uuid.uuid4().hex, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    recommendation_percent  = Column(Integer, index=True)
    summary_positive = Column(String, index=True)
    summary_negative = Column(String, index=True)
    from_platform = Column(Integer, index=True)
    img_url = Column(String, index=True)