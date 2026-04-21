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

@router.get("/search")
def search(link: str, db: Session = Depends(get_db)):
    # if statement to check url and call the right scrapping function
    if ("itch.io" in link and "https://" in link):
        resultItchio = scrap_itchio(link)
        outputSentiment = [predict_sentiment(r, sentiment_model) for r in resultItchio.get('comments')]
        positiveReviews = [r for r, p in zip(resultItchio.get('comments'), outputSentiment) if p == "LABEL_1"]
        negativeReviews = [r for r, p in zip(resultItchio.get('comments'), outputSentiment) if p == "LABEL_0"]
        
        # PENTING: Validasi sebelum summarization
        positiveSummary = None
        negativeSummary = None
        
        if positiveReviews:  # Cek apakah ada positive reviews
            positiveTopTen = " ".join(positiveReviews[:10])
            if len(positiveTopTen) > 50:  # Minimum 50 karakter
                try:
                    positiveSummary = summarization_pipeline(positiveTopTen[:1000], max_length=100, min_length=10, do_sample=False)
                    positiveSummary = positiveSummary[0]['summary_text']
                except Exception as e:
                    print(f"Error summarizing positive: {str(e)}")
                    positiveSummary = positiveTopTen[:100]  # Fallback ke text original (potong)
            else:
                positiveSummary = positiveTopTen
        else:
            positiveSummary = "No positive reviews found"
        
        if negativeReviews:  # Cek apakah ada negative reviews
            negativeTopTen = " ".join(negativeReviews[:10])
            if len(negativeTopTen) > 50:  # Minimum 50 karakter
                try:
                    negativeSummary = summarization_pipeline(negativeTopTen[:1000], max_length=100, min_length=10, do_sample=False)
                    negativeSummary = negativeSummary[0]['summary_text']
                except Exception as e:
                    print(f"Error summarizing negative: {str(e)}")
                    negativeSummary = negativeTopTen[:100]  # Fallback
            else:
                negativeSummary = negativeTopTen
        else:
            negativeSummary = "No negative reviews found"
        
        # get image url from rawg api using the game title
        img_url = None
        try:
            rawg_api_key = os.getenv("RAWG_APIKEY")
            rawg_url = f"https://api.rawg.io/api/games?key={rawg_api_key}&search=NARAKA%20BLADEPOINT&page_size=1"
            rawg_response = requests.get(rawg_url, timeout=10)
            if rawg_response.status_code == 200:
                rawg_data = rawg_response.json()
                if rawg_data.get("results"):
                    img_url = rawg_data["results"][0].get("background_image")
        except Exception as e:
            print(f"Error fetching image from RAWG: {str(e)}")
        
        # save to database if not exist
        if (new_game := db.query(Game).filter(Game.name == resultItchio.get('title')).first()) is None:
            new_game = Game(
                name=resultItchio.get('title'), 
                description="From Itch.io", 
                recommendation_percent=((len(positiveReviews) / (len(negativeReviews) + len(positiveReviews))) * 100) if (len(negativeReviews) + len(positiveReviews)) > 0 else 0,
                summary_positive=positiveSummary,
                summary_negative=negativeSummary,
                from_platform=1,
                img_url=img_url
            )
            db.add(new_game)
            db.commit()
            db.refresh(new_game)
        
        return [{
            'game_id': 1,
            'name': resultItchio.get('title'),
            'description': "From Itch.io",
            'recommendation_percent': ((len(positiveReviews) / (len(negativeReviews) + len(positiveReviews))) * 100) if (len(negativeReviews) + len(positiveReviews)) > 0 else 0,
            'summary_positive': positiveSummary,
            'summary_negative': negativeSummary,
            'from_platform': 1,
            'img_url': img_url
        }]
    elif ("play.google.com" in link and "https://" in link):
        resultPlayStore = scrap_google_play(link)
        outputSentiment = [predict_sentiment(r, sentiment_model) for r in resultPlayStore.get('comments')]
        positiveReviews = [r for r, p in zip(resultPlayStore.get('comments'), outputSentiment) if p == "LABEL_1"]
        negativeReviews = [r for r, p in zip(resultPlayStore.get('comments'), outputSentiment) if p == "LABEL_0"]
        
        # summarize 10 reviews per category
        positiveTopTen = " ".join(positiveReviews[:10])
        negativeTopTen = " ".join(negativeReviews[:10])
        
        if positiveReviews:
            if len(positiveTopTen) > 50:
                try:
                    positiveSummary = summarization_pipeline(positiveTopTen[:1000], max_length=100, min_length=10, do_sample=False)
                    positiveSummary = positiveSummary[0]['summary_text']
                except Exception as e:
                    print(f"Error summarizing positive: {str(e)}")
                    positiveSummary = positiveTopTen[:100]
            else:
                positiveSummary = positiveTopTen
        else:
            positiveSummary = "No positive reviews found"
        
        if negativeReviews:
            if len(negativeTopTen) > 50:
                try:
                    negativeSummary = summarization_pipeline(negativeTopTen[:1000], max_length=100, min_length=10, do_sample=False)
                    negativeSummary = negativeSummary[0]['summary_text']
                except Exception as e:
                    print(f"Error summarizing negative: {str(e)}")
                    negativeSummary = negativeTopTen[:100]
            else:
                negativeSummary = negativeTopTen
        else:
            negativeSummary = "No negative reviews found"
            
        # get image url from rawg api using the game title
        img_url = None
        try:
            rawg_api_key = os.getenv("RAWG_APIKEY")
            rawg_url = f"https://api.rawg.io/api/games?key={rawg_api_key}&search=NARAKA%20BLADEPOINT&page_size=1"
            rawg_response = requests.get(rawg_url, timeout=10)
            if rawg_response.status_code == 200:
                rawg_data = rawg_response.json()
                if rawg_data.get("results"):
                    img_url = rawg_data["results"][0].get("background_image")
        except Exception as e:
            print(f"Error fetching image from RAWG: {str(e)}")
        
        # save to database if not exist
        if (new_game := db.query(Game).filter(Game.name == resultPlayStore.get('title')).first()) is None:
            new_game = Game(
                name=resultPlayStore.get('title'), 
                description="From Google Play", 
                recommendation_percent=((len(positiveReviews) / (len(negativeReviews) + len(positiveReviews))) * 100), 
                summary_positive=positiveSummary, 
                summary_negative=negativeSummary, 
                from_platform=2,
                img_url=img_url
            )
            db.add(new_game)
            db.commit()
            db.refresh(new_game)
        
        return [{
            'game_id': 1,
            'name': resultPlayStore.get('title'),
            'description': "From Google Play",
            'recommendation_percent': ((len(positiveReviews) / (len(negativeReviews) + len(positiveReviews))) * 100),
            'summary_positive': positiveSummary,
            'summary_negative': negativeSummary,
            'from_platform': 2,
            'img_url': img_url
        }]
    elif ("store.steampowered.com" in link and "https://" in link):
        resultSteam = scrap_steam(link)
        outputSentiment = [predict_sentiment(r, sentiment_model) for r in resultSteam.get('comments')]
        positiveReviews = [r for r, p in zip(resultSteam.get('comments'), outputSentiment) if p == "LABEL_1"]
        negativeReviews = [r for r, p in zip(resultSteam.get('comments'), outputSentiment) if p == "LABEL_0"]
        
        # summarize 10 reviews per category
        positiveTopTen = " ".join(positiveReviews[:10])
        negativeTopTen = " ".join(negativeReviews[:10])
        
        if positiveReviews:
            if len(positiveTopTen) > 50:
                try:
                    positiveSummary = summarization_pipeline(positiveTopTen[:1000], max_length=100, min_length=10, do_sample=False)
                    positiveSummary = positiveSummary[0]['summary_text']
                except Exception as e:
                    print(f"Error summarizing positive: {str(e)}")
                    positiveSummary = positiveTopTen[:100]
            else:
                positiveSummary = positiveTopTen
        else:
            positiveSummary = "No positive reviews found"
            
        if negativeReviews:
            if len(negativeTopTen) > 50:
                try:
                    negativeSummary = summarization_pipeline(negativeTopTen[:1000], max_length=100, min_length=10, do_sample=False)
                    negativeSummary = negativeSummary[0]['summary_text']
                except Exception as e:
                    print(f"Error summarizing negative: {str(e)}")
                    negativeSummary = negativeTopTen[:100]
            else:
                negativeSummary = negativeTopTen
        else:
            negativeSummary = "No negative reviews found"
        
        # get image url from rawg api using the game title
        img_url = None
        try:
            rawg_api_key = os.getenv("RAWG_APIKEY")
            rawg_url = f"https://api.rawg.io/api/games?key={rawg_api_key}&search=NARAKA%20BLADEPOINT&page_size=1"
            rawg_response = requests.get(rawg_url, timeout=10)
            if rawg_response.status_code == 200:
                rawg_data = rawg_response.json()
                if rawg_data.get("results"):
                    img_url = rawg_data["results"][0].get("background_image")
        except Exception as e:
            print(f"Error fetching image from RAWG: {str(e)}")

        # save to database if not exist
        if (new_game := db.query(Game).filter(Game.name == resultSteam.get('title')).first()) is None:
            new_game = Game(
                name=resultSteam.get('title'), 
                description="From Steam", 
                recommendation_percent=((len(positiveReviews) / (len(negativeReviews) + len(positiveReviews))) * 100), 
                summary_positive=positiveSummary, 
                summary_negative=negativeSummary, 
                from_platform=3, 
                img_url=img_url
            )
            db.add(new_game)
            db.commit()
            db.refresh(new_game)
        
        return [
            {
                'game_id': 1,
                'name': resultSteam.get('title'),
                'description': "From Steam",
                'recommendation_percent': ((len(positiveReviews) / (len(negativeReviews) + len(positiveReviews))) * 100),
                'summary_positive': positiveSummary,
                'summary_negative': negativeSummary,
                'from_platform': 3,
                'img_url': img_url
            }
        ]
    else:
        games = db.query(Game).filter(Game.name.ilike(f"%{link}%")).all()
        
        if not games:
            return {
                "message": "Game not found. Please provide a valid link from Itch.io, Google Play, or Steam to analyze."
            }
            
        return games
    
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
def scrap_google_play(link: str):
    app_id = link.split("id=")[1]
    resultReview, token = playStoreReviews(app_id=app_id, lang="en", country="us", sort=playStoreSort.NEWEST, count=100)
    resultApp = playStoreAppDetail(app_id=app_id, lang="en", country="us")
    
    contents = [review['content'] for review in resultReview]
    
    return {'title': resultApp.get('title'), 'comments': contents}

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
    