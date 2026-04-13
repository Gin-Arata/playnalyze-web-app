from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models.database import engine, Base
from ..models.items import Item
from ..models.deps import get_db

router = APIRouter(prefix="/items", tags=["items"])

Base.metadata.create_all(bind=engine)

@router.get("/")
def get_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return items