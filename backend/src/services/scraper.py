import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

import requests
import feedparser
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
import logging
from src.services.sentiment_analyzer import SentimentAnalyzer
from src.services.llm_processor import LLMProcessor
from src.database import SessionLocal
from src.models import Article

logger = logging.getLogger(__name__)

class RSSScraper:
    RSS_FEEDS = {
        "économie": {
            "lesechos": "https://news.google.com/rss/search?q=site:lesechos.fr+économie&hl=fr&gl=FR&ceid=FR:fr",
            "latribune": "https://news.google.com/rss/search?q=site:latribune.fr+économie&hl=fr&gl=FR&ceid=FR:fr",
        },
        "climat": {
            "lemonde_planete": "https://www.lemonde.fr/planete/rss_full.xml",
            "reporterre": "https://reporterre.net/spip.php?page=backend",
        },
        "politique": {
            "lefigaro_pol": "https://www.lefigaro.fr/rss/figaro_politique.xml",
            "liberation_pol": "https://www.liberation.fr/arc/outboundfeeds/rss/category/politique/",
        },
        "géopolitique": {
            "courrierinter": "https://www.courrierinternational.com/feed/all/rss.xml",
            "diploweb": "https://www.diploweb.com/spip.php?page=backend",
        },
        "sport": {
            "lequipe": "https://www.lequipe.fr/rss/actu_rss.xml",
            "rmc_sport": "https://rmcsport.bfmtv.com/rss/fil-info/",
        }
    }

    def __init__(self, max_articles_per_topic: int = 10):
        self.max_articles_per_topic = max_articles_per_topic
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "BotActu/1.0"})
        self.analyzer = SentimentAnalyzer()
        self.llm_processor = LLMProcessor()
        self.db = SessionLocal()

    def fetch_article_text(self, url: str) -> str:
        try:
            r = self.session.get(url, timeout=4)
            if r.status_code != 200: return ""
            soup = BeautifulSoup(r.text, "html.parser")
            tags = ["article", "main", "div.content", "div.post-content", "div#content"]
            for t in tags:
                c = soup.select_one(t)
                if c: return c.get_text(" ", strip=True)
            return ""
        except:
            return ""

    def article_exists(self, url: str) -> bool:
        return self.db.query(Article).filter(Article.url == url).first() is not None

    def save_to_db(self, data: dict):
        try:
            self.db.add(Article(**data))
            self.db.commit()
        except:
            self.db.rollback()

    def scrape_topic(self, topic: str, query: str = None) -> List[Article]:
        new_articles_found = []
        feeds = self.RSS_FEEDS.get(topic, {})
        MAX_PER_SOURCE = 2 
        
        for feed_name, feed_url in feeds.items():
            feed = feedparser.parse(feed_url)
            if feed.bozo: continue
            
            source_count = 0 
            for entry in feed.entries:
                if source_count >= MAX_PER_SOURCE: break
                link = entry.link
                if self.article_exists(link): continue

                try:
                    full_text = self.fetch_article_text(link)
                    
                    # --- FILTRE INTELLIGENT ---
                    if query:
                        q_low = query.lower()
                        if q_low not in entry.title.lower() and q_low not in full_text.lower():
                            continue 
                    # --------------------------

                    txt_analyze = full_text if len(full_text) > 100 else entry.title
                    s_score, s_label = self.analyzer.analyze(txt_analyze)
                    
                    ai_sum, rel, srcs = "Non disponible", 50, 0
                    if len(full_text) > 300:
                        analysis = self.llm_processor.analyze_content(full_text)
                        if analysis:
                            ai_sum, rel, srcs = analysis.summary, analysis.reliability_score, len(analysis.sources)

                    article_data = {
                        "title": entry.title,
                        "url": link,
                        "source": feed_name,
                        "topic": topic,
                        "published_date": datetime.now(),
                        "content": full_text[:5000],
                        "sentiment_score": s_score,
                        "sentiment_label": s_label,
                        "summary": ai_sum,
                        "reliability_score": rel,
                        "source_count": srcs
                    }
                    self.save_to_db(article_data)
                    new_articles_found.append(Article(**article_data))
                    source_count += 1
                    
                except Exception as e:
                    logger.error(f"Erreur: {e}")
                    continue
                    
        return new_articles_found