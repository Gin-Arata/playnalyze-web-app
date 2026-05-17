import requests
import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models.database import engine, Base
from ..models.games import Game
from ..models.deps import get_db
from bs4 import BeautifulSoup
from google_play_scraper import app as playStoreAppDetail, reviews as playStoreReviews, Sort as playStoreSort
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/games", tags=["games"])

Base.metadata.create_all(bind=engine)

model_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../app/ai_models/steam_review_model")
)

print("Loading sentiment model...")
sentiment_model = pipeline("text-classification", model=model_dir, tokenizer="distilbert-base-uncased", device=0)

print("Loading summarization model...")
summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn", device=0)

@router.get("/")
def get_all_games(db: Session = Depends(get_db)):
    games = db.query(Game).all()
    return games

def __generate_summary(reviews: list, category_name: str) -> str:
    if not reviews:
        return f"No {category_name} reviews found"
        
    top_ten = " ".join(reviews[:10])
    if len(top_ten) > 50:
        try:
            summary = summarization_pipeline(top_ten[:1000], max_length=100, min_length=10, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            print(f"Error summarizing {category_name}: {str(e)}")
            return top_ten[:100]
    return top_ten

def __fetch_game_image(title: str):
    try:
        rawg_api_key = os.getenv("RAWG_APIKEY")
        rawg_url = f"https://api.rawg.io/api/games?key={rawg_api_key}&search={title}&page_size=1"
        rawg_response = requests.get(rawg_url, timeout=10)
        if rawg_response.status_code == 200:
            rawg_data = rawg_response.json()
            if rawg_data.get("results"):
                return rawg_data["results"][0].get("background_image")
    except Exception as e:
        print(f"Error fetching image from RAWG: {str(e)}")
    return None

@router.get("/search")
def search(link: str, db: Session = Depends(get_db)):
    # Check if game is already in db by URL
    if "https://" in link:
        games = db.query(Game).filter(Game.game_url == link).all()
        if games:
            return games
    
    # Identify platform and scrape
    platform_id = None
    scraped_data = {}
    
    if "itch.io" in link and "https://" in link:
        platform_id = 1
        scraped_data = scrap_itchio(link)
    elif "play.google.com" in link and "https://" in link:
        platform_id = 2
        scraped_data = scrap_google_play(link)
    elif "store.steampowered.com" in link and "https://" in link:
        platform_id = 3
        scraped_data = scrap_steam(link)
    else:
        # Fallback to DB search by game title
        games = db.query(Game).filter(Game.name.ilike(f"%{link}%")).all()
        if not games:
            return {"message": "Game not found. Please provide a valid link from Itch.io, Google Play, or Steam to analyze."}
        return games
    
    title = scraped_data.get('title')
    description = scraped_data.get('description')
    comments = scraped_data.get('comments', [])
    
    # Process reviews sentiment
    outputSentiment = [predict_sentiment(r, sentiment_model) for r in comments]
    positiveReviews = [r for r, p in zip(comments, outputSentiment) if p == "LABEL_1"]
    negativeReviews = [r for r, p in zip(comments, outputSentiment) if p == "LABEL_0"]
    
    positiveSummary = __generate_summary(positiveReviews, "positive")
    negativeSummary = __generate_summary(negativeReviews, "negative")
    
    # Fetch image 
    img_url = __fetch_game_image(title) if platform_id in [2, 3] else None
        
    total_reviews = len(positiveReviews) + len(negativeReviews)
    recommendation_percent = round((len(positiveReviews) / total_reviews) * 100) if total_reviews > 0 else 0
    
    # Save to database if not exists
    if (new_game := db.query(Game).filter(Game.name == title).first()) is None:
        new_game = Game(
            name=title, 
            description=description, 
            recommendation_percent=recommendation_percent,
            summary_positive=positiveSummary,
            summary_negative=negativeSummary,
            from_platform=platform_id,
            img_url=img_url,
            game_url=link
        )
        db.add(new_game)
        db.commit()
        db.refresh(new_game)
    
    return [{
        'game_id': 1,
        'name': title,
        'description': description,
        'recommendation_percent': recommendation_percent,
        'summary_positive': positiveSummary,
        'summary_negative': negativeSummary,
        'from_platform': platform_id,
        'img_url': img_url,
        'game_url': link
    }]
    
def predict_sentiment(text, sentiment_model):
    words = text.split()
    if len(words) > 512:
        text = " ".join(words[:512])
    
    try:
        result = sentiment_model(text, truncation=True, max_length=512)
        return result[0]['label']
    except Exception as e:
        print(f"Error predicting: {str(e)[:50]}...")
        return "LABEL_0"

# Scrapping itch.io
def scrap_itchio(link: str):
    url = link
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    gameTitle = soup.find("h1", class_="game_title").text.strip()
    gameDescription = soup.find("div", class_="formatted_description").text.strip()
    commentsPage1 = soup.find_all("div", class_="post_body")
    
    totalComments = soup.find("nobr")
    
    if (not totalComments):
        return {"title": gameTitle, "description": gameDescription, "comments": [c.text.strip() for c in commentsPage1]}
    else:
        textTotalComments = totalComments.text.strip()
        partsTotalComments = textTotalComments.split(" ")
        currentTotalComments = int(partsTotalComments[2]) - 1
        total = int(partsTotalComments[4])
        res = requests.get(url + "/comments?before=" + str(total - currentTotalComments), headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        commentsPage2 = soup.find_all("div", class_="post_body")
        
        allComments = commentsPage1 + commentsPage2
        return {"title": gameTitle, "description": gameDescription, "comments": [c.text.strip() for c in allComments]}
    
# Scrapping Google Play
def scrap_google_play(link: str):
    app_id = link.split("id=")[1]
    resultReview, token = playStoreReviews(app_id=app_id, lang="en", country="us", sort=playStoreSort.NEWEST, count=100)
    resultApp = playStoreAppDetail(app_id=app_id, lang="en", country="us")
    
    contents = [review['content'] for review in resultReview]
    
    return {'title': resultApp.get('title'), 'description': resultApp.get('description'), 'comments': contents}

# request api steam
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
        description = None
        if appid in details_data and details_data[appid].get("success"):
            title = details_data[appid]["data"].get("name", "Unknown")
            description = details_data[appid]["data"].get("short_description", "No description available")
        
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
            "description": description,
            "comments": comments
        }
    
    except Exception as e:
        print(f"Error scraping Steam: {str(e)}")
        return {"title": None, "description": None, "comments": [], "error": str(e)}
    