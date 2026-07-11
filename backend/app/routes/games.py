import requests
import os
import re
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
    os.path.join(os.path.dirname(__file__), "../../app/ai_models/steam_review_model2")
)

print("Loading sentiment model...")
sentiment_model = pipeline("text-classification", model=model_dir, tokenizer="distilbert-base-uncased", device=0)

print("Loading summarization model...")
summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn", device=0)

@router.get("/")
def get_all_games(db: Session = Depends(get_db)):
    games = db.query(Game).all()
    return games

def text_preprocessing(text: str) -> str:
    # Case folding
    text = text.lower()
    
    # Noise removal
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE) # Hapus URL
    text = re.sub(r'<.*?>', '', text) # Hapus tag HTML
    text = re.sub(r'[^\x00-\x7f]', '', text) # Hapus karakter non-ASCII
    text = re.sub(r'\s+', ' ', text).strip() # Menghapus spasi berlebih
    
    # Normalisasi
    norm_dict = {
        "gg": "good game", "ez": "easy", "p2w": "pay to win",
        "recomended": "recommended", "rekomended": "recommended",
        "u": "you", "r": "are", "duud": "dude", "op": "overpowered",
        "fk": "fuck", "p2p": "peer to peer", "ths": "this", "thx": "thanks",
    }
    
    words = text.split()
    normalized_words = [norm_dict.get(word, word) for word in words]
    return " ".join(normalized_words)

def clean_review_markup(text: str) -> str:
    # Hapus template kotak centang [ ] atau ☑ agar tidak membingungkan summarizer
    text = re.sub(r'☐|☑|---{|}|---', '', text)
    return text[:1500]

def __generate_summary(reviews_text: str, category_name: str) -> str:
    if not reviews_text.strip():
        return f"No {category_name} reviews found"
        
    clean_text = clean_review_markup(reviews_text)
    
    if len(clean_text) > 100:
        try:
            summary = summarization_pipeline(clean_text, max_length=150, min_length=40, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            print(f"Error summarizing {category_name}: {str(e)}")
            return clean_text[:150]
    return f"Ulasan {category_name} terlalu pendek."

def predict_sentiment_with_score(text: str, max_length=512):
    words = text.split()
    if len(words) > max_length:
        text = " ".join(words[:max_length])
    
    try:
        result = sentiment_model(text, truncation=True, max_length=max_length)
        return result[0]['label'], result[0]['score']
    except Exception as e:
        print(f"Error predicting: {str(e)[:50]}...")
        return "LABEL_0", 0.0

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
    preprocessed_reviews = [text_preprocessing(r) for r in comments]
    
    full_predictions = []
    for orig, prep in zip(comments, preprocessed_reviews):
        label, score = predict_sentiment_with_score(prep)
        full_predictions.append({'text': orig, 'label': label, 'score': score})
    
    # Sort reviews by confidence score
    positive_list = sorted([p for p in full_predictions if p['label'] == "LABEL_1"], 
                           key=lambda x: x['score'], reverse=True)
    negative_list = sorted([p for p in full_predictions if p['label'] == "LABEL_0"], 
                           key=lambda x: x['score'], reverse=True)
    
    # Gather top texts (filter out "masterpiece" for negative)
    positive_text = " ".join([p['text'] for p in positive_list[:10]])
    negative_text = " ".join([p['text'] for p in negative_list[:10]])
    
    # Generate Summaries
    positiveSummary = __generate_summary(positive_text, "positive")
    negativeSummary = __generate_summary(negative_text, "negative")
    
    # Fetch image 
    img_url = __fetch_game_image(title) if platform_id in [2, 3] else None
        
    total_reviews = len(positive_list) + len(negative_list)
    recommendation_percent = round((len(positive_list) / total_reviews) * 100) if total_reviews > 0 else 0
    
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
        reviews_url = f"https://store.steampowered.com/appreviews/{appid}?json=1&filter=recent&num_per_page=100"
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
    