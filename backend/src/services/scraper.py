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
from src.services.news_api_service import NewsAPIService  # ← NOUVEAU
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
            # ✅ URLS CORRIGÉES (les anciennes étaient en 404)
            "google_sport": "https://news.google.com/rss/search?q=sport&hl=fr&gl=FR&ceid=FR:fr",
            "google_tennis": "https://news.google.com/rss/search?q=tennis&hl=fr&gl=FR&ceid=FR:fr",
            "20minutes_sport": "https://www.20minutes.fr/feeds/rss-sport.xml",
        }
    }

    def __init__(self, max_articles_per_topic: int = 10):
        self.max_articles_per_topic = max_articles_per_topic
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "BotActu/1.0"})
        self.analyzer = SentimentAnalyzer()
        self.llm_processor = LLMProcessor()
        self.db = SessionLocal()
        self.news_api = NewsAPIService()  # ← NOUVEAU : Service NewsAPI

    def fetch_article_text(self, url: str) -> str:
        """Récupère le contenu textuel d'un article depuis son URL"""
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
        """Vérifie si un article existe déjà en base de données"""
        return self.db.query(Article).filter(Article.url == url).first() is not None

    def save_to_db(self, data: dict):
        """Sauvegarde un article en base de données"""
        try:
            self.db.add(Article(**data))
            self.db.commit()
        except:
            self.db.rollback()

    def scrape_topic(self, topic: str, query: str = None) -> List[Article]:
        """
        Scrape les articles pour un sujet donné
        
        Args:
            topic: Sujet à scraper (économie, climat, politique, géopolitique, sport)
            query: Mot-clé de recherche optionnel (ex: "tennis", "Biden")
            
        Returns:
            Liste des nouveaux articles trouvés
        """
        new_articles_found = []
        
        # ═══════════════════════════════════════════════════════════════
        # PRIORITÉ 1 : NewsAPI (si query fournie)
        # ═══════════════════════════════════════════════════════════════
        if query and self.news_api.client:
            print(f"   🔍 Recherche NewsAPI pour '{query}'...")
            api_articles = self.news_api.search_articles(query, max_results=5)
            
            for art_data in api_articles:
                # Vérifier si l'article existe déjà
                if self.article_exists(art_data['url']):
                    continue
                
                try:
                    # Analyse du sentiment
                    text_to_analyze = art_data.get('description', '') or art_data['title']
                    s_score, s_label = self.analyzer.analyze(text_to_analyze)
                    
                    # Analyse LLM (résumé + sources) si contenu disponible
                    content = art_data.get('content', '')
                    ai_sum, rel, srcs = "Non disponible", 50, 0
                    if len(content) > 300:
                        analysis = self.llm_processor.analyze_content(content)
                        if analysis:
                            ai_sum = analysis.summary
                            rel = analysis.reliability_score
                            srcs = len(analysis.sources)
                    
                    # Créer l'objet article
                    article_data = {
                        "title": art_data['title'],
                        "url": art_data['url'],
                        "source": art_data['source'],
                        "topic": topic,
                        "published_date": datetime.now(),
                        "content": content[:5000],
                        "sentiment_score": s_score,
                        "sentiment_label": s_label,
                        "summary": ai_sum,
                        "reliability_score": rel,
                        "source_count": srcs
                    }
                    
                    # Sauvegarder en DB
                    self.save_to_db(article_data)
                    new_articles_found.append(Article(**article_data))
                    print(f"      ✅ NewsAPI: {art_data['title'][:60]}...")
                    
                except Exception as e:
                    logger.error(f"Erreur traitement article NewsAPI: {e}")
                    continue
        
        # ═══════════════════════════════════════════════════════════════
        # PRIORITÉ 2 : RSS Feeds (backup / complément)
        # ═══════════════════════════════════════════════════════════════
        feeds = self.RSS_FEEDS.get(topic, {})
        MAX_PER_SOURCE = 5  # Limite par source pour diversifier
        
        for feed_name, feed_url in feeds.items():
            feed = feedparser.parse(feed_url)
            if feed.bozo: 
                continue  # Flux RSS malformé, on passe
            
            source_count = 0
            for entry in feed.entries:
                if source_count >= MAX_PER_SOURCE: 
                    break  # On a assez pour cette source
                
                link = entry.link
                if self.article_exists(link): 
                    continue  # Article déjà en base

                try:
                    # Récupération du contenu complet
                    full_text = self.fetch_article_text(link)
                    
                    # --- FILTRE PAR MOT-CLÉ ---
                    if query:
                        q_low = query.lower()
                        if q_low not in entry.title.lower() and q_low not in full_text.lower():
                            continue  # Article ne contient pas le mot-clé
                    
                    # Analyse du sentiment
                    txt_analyze = full_text if len(full_text) > 100 else entry.title
                    s_score, s_label = self.analyzer.analyze(txt_analyze)
                    
                    # Analyse LLM (résumé + sources)
                    ai_sum, rel, srcs = "Non disponible", 50, 0
                    if len(full_text) > 300:
                        analysis = self.llm_processor.analyze_content(full_text)
                        if analysis:
                            ai_sum = analysis.summary
                            rel = analysis.reliability_score
                            srcs = len(analysis.sources)

                    # Créer l'objet article
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
                    
                    # Sauvegarder en DB
                    self.save_to_db(article_data)
                    new_articles_found.append(Article(**article_data))
                    source_count += 1
                    
                except Exception as e:
                    logger.error(f"Erreur RSS: {e}")
                    continue
                    
        return new_articles_found
