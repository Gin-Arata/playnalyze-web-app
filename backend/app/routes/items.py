import requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models.database import engine, Base
from ..models.items import Item
from ..models.deps import get_db
from bs4 import BeautifulSoup
from google_play_scraper import reviews as playStoreReviews, Sort as playStoreSort

router = APIRouter(prefix="/items", tags=["items"])

Base.metadata.create_all(bind=engine)

@router.get("/")
def get_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return items

# Scrapping itch.io
@router.get("/scrap-itchio")
def scrap_test(link: str):
    url = link
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    commentsPage1 = soup.find_all("div", class_="post_body")
    
    totalComments = soup.find("nobr")
    
    if (not totalComments):
        return {"total_comments": len(commentsPage1), "comments": [c.text.strip() for c in commentsPage1]}
    else:
        textTotalComments = totalComments.text.strip()
        partsTotalComments = textTotalComments.split(" ")
        currentTotalComments = int(partsTotalComments[2]) - 1
        total = int(partsTotalComments[4])
        res = requests.get(url + "/comments?before=" + str(total - currentTotalComments), headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        commentsPage2 = soup.find_all("div", class_="post_body")
        
        allComments = commentsPage1 + commentsPage2
        return {"total_comments": total, "comments": [c.text.strip() for c in allComments]}
    
# Scrapping Google Play
@router.get("/scrap-google-play")
def scrap_google_play(link: str):
    app_id = link.split("id=")[1]
    result, token = playStoreReviews(app_id=app_id, lang="en", country="us", sort=playStoreSort.NEWEST, count=100)
    
    contents = [review['content'] for review in result]
    
    return {"total_comments": len(contents), "comments": contents}

# request api steam
@router.get("/scrap-steam")
def scrap_steam(link: str):
    print("test")