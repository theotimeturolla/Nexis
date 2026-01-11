import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

import logging
from typing import List
from datetime import datetime
from src.services.sentiment_analyzer import SentimentAnalyzer
from src.services.llm_processor import LLMProcessor
from src.services.news_api_service import NewsAPIService
from src.services.importance_ranker import ImportanceRanker  
from src.database import SessionLocal
from src.models import Article

logger = logging.getLogger(__name__)

class RSSScraper:
    # 🗑️ SUPPRESSION DE RSS_FEEDS (plus de liens https en dur)

    def __init__(self, max_articles_per_topic: int = 10):
        self.max_articles_per_topic = max_articles_per_topic
        self.analyzer = SentimentAnalyzer()
        self.llm_processor = LLMProcessor()
        self.db = SessionLocal()
        self.news_api = NewsAPIService()
        self.ranker = ImportanceRanker()  

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
        Scrape les articles uniquement via NewsAPI.
        Si 'query' est vide, on utilise 'topic' comme mot-clé de recherche.
        Les articles sont ensuite triés par importance avec Gemini AI.
        """
        new_articles_found = []
        
        # Stratégie : Si pas de mot-clé précis, on cherche le sujet global
        search_term = query if query else topic
        
        if not self.news_api.client:
            print("❌ Erreur : NewsAPI n'est pas initialisé (Clé API manquante ?)")
            return []

        print(f"   🔍 Recherche NewsAPI pour '{search_term}' (Sujet: {topic})...")
        
        # On récupère plus d'articles pour que Gemini ait le choix
        max_fetch = max(20, self.max_articles_per_topic * 2)
        api_articles = self.news_api.search_articles(search_term, max_results=max_fetch)
        
        print(f"📰 NewsAPI a retourné {len(api_articles)} articles")  # DEBUG
        
        for i, art_data in enumerate(api_articles, 1):
            print(f"\n   [{i}/{len(api_articles)}] Traitement: {art_data['title'][:50]}...")  # DEBUG
            
            # Vérifier si l'article existe déjà
            if self.article_exists(art_data['url']):
                print(f"      ⏭️ Déjà en base, skip")  # DEBUG
                continue
            
            try:
                # 1. Analyse du sentiment (sur description ou titre)
                text_to_analyze = art_data.get('description', '') or art_data['title']
                print(f"      🔄 Analyse sentiment...")  # DEBUG
                s_score, s_label = self.analyzer.analyze(text_to_analyze)
                print(f"      ✅ Sentiment: {s_label} ({s_score:.2f})")  # DEBUG
                
                # 2. Analyse LLM (résumé + sources)
                content = art_data.get('content', '') or art_data.get('description', '') or ""
                ai_sum, rel, srcs = "Non disponible", 50, 0
                
                if len(content) > 200:
                    print(f"      🔄 Analyse LLM...")  # DEBUG
                    analysis = self.llm_processor.analyze_content(content)
                    if analysis:
                        ai_sum = analysis.summary
                        rel = analysis.reliability_score
                        srcs = len(analysis.sources)
                        print(f"      ✅ Résumé généré")  # DEBUG
                
                # 3. Création de l'objet article
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
                
                # 4. Sauvegarde
                print(f"      💾 Sauvegarde en DB...")  # DEBUG
                self.save_to_db(article_data)
                print(f"      ✅ Sauvegardé en DB")  # DEBUG
                
                new_articles_found.append(Article(**article_data))
                print(f"      ➕ Ajouté à la liste (total: {len(new_articles_found)})")  # DEBUG
                
            except Exception as e:
                print(f"      ❌ ERREUR: {e}")  # DEBUG
                import traceback
                traceback.print_exc()  # DEBUG
                continue
        
        print(f"\n📊 Total articles collectés: {len(new_articles_found)}")  # DEBUG
        
        # SÉLECTION INTELLIGENTE avec Gemini
        if len(new_articles_found) > self.max_articles_per_topic:
            print(f"🤖 Gemini sélectionne les {self.max_articles_per_topic} meilleurs articles...")
            print(f"   📥 Envoi de {len(new_articles_found)} articles à Gemini")  # DEBUG
            
            new_articles_found = self.ranker.rank_articles(
                new_articles_found, 
                top_n=self.max_articles_per_topic
            )
            
            print(f"   📤 Gemini a retourné {len(new_articles_found)} articles")  # DEBUG
        
        print(f"\n✅ Retour final: {len(new_articles_found)} articles")  # DEBUG
        return new_articles_found