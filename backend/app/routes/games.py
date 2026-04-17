import requests
import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models.database import engine, Base
from ..models.items import Item
from ..models.deps import get_db
from bs4 import BeautifulSoup
from google_play_scraper import app as playStoreAppDetail, reviews as playStoreReviews, Sort as playStoreSort
from transformers import pipeline

router = APIRouter(prefix="/items", tags=["items"])

Base.metadata.create_all(bind=engine)

@router.get("/")
def get_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return items

@router.get("/predict")
def predict(link: str):
    model_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../app/ai_models/steam_review_model")
    )
    # add sentiment model
    sentiment_model = pipeline("text-classification", model=model_dir, tokenizer="distilbert-base-uncased", device=0)

    # pipeline for summarization
    summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn", device=0)
    
    # if statement to check url and call the right scrapping function
    if ("itch.io" in link):
        resultItchio = scrap_itchio(link)
        outputSentiment = [predict_sentiment(r, sentiment_model) for r in resultItchio.get('comments')]
        positiveReviews = [r for r, p in zip(resultItchio.get('comments'), outputSentiment) if p == "LABEL_1"]
        negativeReviews = [r for r, p in zip(resultItchio.get('comments'), outputSentiment) if p == "LABEL_0"]
        
        # summarize 10 reviews per category
        positiveTopTen = " ".join(positiveReviews[:10])
        negativeTopTen = " ".join(negativeReviews[:10])
        positiveSummary = summarization_pipeline(positiveTopTen[:4000], max_length=100, min_length=10, do_sample=False)
        negativeSummary = summarization_pipeline(negativeTopTen[:4000], max_length=100, min_length=10, do_sample=False)
        
        return {
            'title': resultItchio.get('title'),
            'percentageRecommendation': ((len(positiveReviews) / (len(negativeReviews) + len(positiveReviews))) * 100),
            'positiveSummary': positiveSummary,
            'negativeSummary': negativeSummary
        }
    elif ("play.google.com" in link):
        resultPlayStore = scrap_google_play(link)
        outputSentiment = [predict_sentiment(r, sentiment_model) for r in resultPlayStore.get('comments')]
        positiveReviews = [r for r, p in zip(resultPlayStore.get('comments'), outputSentiment) if p == "LABEL_1"]
        negativeReviews = [r for r, p in zip(resultPlayStore.get('comments'), outputSentiment) if p == "LABEL_0"]
        
        # summarize 10 reviews per category
        positiveTopTen = " ".join(positiveReviews[:10])
        negativeTopTen = " ".join(negativeReviews[:10])
        positiveSummary = summarization_pipeline(positiveTopTen[:4000], max_length=400, min_length=100, do_sample=False)
        negativeSummary = summarization_pipeline(negativeTopTen[:4000], max_length=400, min_length=100, do_sample=False)
        
        return {
            'title': resultPlayStore.get('title'),
            'percentageRecommendation': ((len(positiveReviews) / (len(negativeReviews) + len(positiveReviews))) * 100),
            'positiveSummary': positiveSummary,
            'negativeSummary': negativeSummary
        }
    elif ("store.steampowered.com" in link):
        resultSteam = scrap_steam(link)
        outputSentiment = [predict_sentiment(r, sentiment_model) for r in resultSteam.get('comments')]
        positiveReviews = [r for r, p in zip(resultSteam.get('comments'), outputSentiment) if p == "LABEL_1"]
        negativeReviews = [r for r, p in zip(resultSteam.get('comments'), outputSentiment) if p == "LABEL_0"]
        
        # summarize 10 reviews per category
        positiveTopTen = " ".join(positiveReviews[:10])
        negativeTopTen = " ".join(negativeReviews[:10])
        positiveSummary = summarization_pipeline(positiveTopTen[:4000], max_length=400, min_length=100, do_sample=False)
        negativeSummary = summarization_pipeline(negativeTopTen[:4000], max_length=400, min_length=100, do_sample=False)
        
        return {
            'title': resultSteam.get('title'),
            'percentageRecommendation': ((len(positiveReviews) / (len(negativeReviews) + len(positiveReviews))) * 100),
            'positiveSummary': positiveSummary,
            'negativeSummary': negativeSummary 
        }
    
def predict_sentiment(text, sentiment_model):
    words = text.split()
    if len(words) > 512:
        text = " ".join(words[:512])
    
    try:
        result = sentiment_model(text, truncation=True, max_length=512)
        return result[0]['label']
    except Exception as e:
        print(f"Error predicting: {str(e)[:50]}...")
        return "LABEL_0"  # Default ke negative jika error

# Scrapping itch.io
@router.get("/scrap-itchio")
def scrap_itchio(link: str):
    url = link
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    gameTitle = soup.find("h1", class_="game_title").text.strip()
    commentsPage1 = soup.find_all("div", class_="post_body")
    
    totalComments = soup.find("nobr")
    
    if (not totalComments):
        return {"title": gameTitle, "comments": [c.text.strip() for c in commentsPage1]}
    else:
        textTotalComments = totalComments.text.strip()
        partsTotalComments = textTotalComments.split(" ")
        currentTotalComments = int(partsTotalComments[2]) - 1
        total = int(partsTotalComments[4])
        res = requests.get(url + "/comments?before=" + str(total - currentTotalComments), headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        commentsPage2 = soup.find_all("div", class_="post_body")
        
        allComments = commentsPage1 + commentsPage2
        return {"title": gameTitle, "comments": [c.text.strip() for c in allComments]}
    
# Scrapping Google Play
@router.get("/scrap-google-play")
def scrap_google_play(link: str):
    app_id = link.split("id=")[1]
    resultReview, token = playStoreReviews(app_id=app_id, lang="en", country="us", sort=playStoreSort.NEWEST, count=100)
    resultApp = playStoreAppDetail(app_id=app_id, lang="en", country="us")
    
    contents = [review['content'] for review in resultReview]
    
    return {'title': resultApp.get('title'), 'comments': contents}

# request api steam
@router.get("/scrap-steam")
def scrap_steam(link: str):
    try:
        # Extract appid from Steam link
        # Format: https://store.steampowered.com/app/{appid} or similar
        appid = link.split("/app/")[1].split("/")[0] if "/app/" in link else None
        
        if not appid:
            return {"error": "Could not extract appid from link", "title": None, "comments": []}
        
        # Fetch game details
        details_url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        details_headers = {
            "User-Agent": "Mozilla/5.0"
        }
        
        details_response = requests.get(details_url, headers=details_headers, timeout=10)
        details_data = details_response.json()
        
        # Get game title
        title = None
        if appid in details_data and details_data[appid].get("success"):
            title = details_data[appid]["data"].get("name", "Unknown")
        
        # Fetch reviews
        reviews_url = f"https://store.steampowered.com/appreviews/{appid}?json=1&day_range=365&num_per_page=100"
        reviews_response = requests.get(reviews_url, headers=details_headers, timeout=10)
        reviews_data = reviews_response.json()
        
        # Extract comments from reviews
        comments = []
        if reviews_data.get("success"):
            reviews_list = reviews_data.get("reviews", [])
            comments = [review.get("review", "") for review in reviews_list if review.get("review")]
        
        return {
            "title": title,
            "comments": comments
        }
    
    except Exception as e:
        print(f"Error scraping Steam: {str(e)}")
        return {"title": None, "comments": [], "error": str(e)}
    