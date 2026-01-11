import os
import sys
from newsapi import NewsApiClient
from datetime import datetime, timedelta
from typing import List
from dotenv import load_dotenv

# Charger le .env depuis le dossier backend
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
dotenv_path = os.path.join(backend_dir, '.env')
load_dotenv(dotenv_path)

class NewsAPIService:
    """Service pour interagir avec NewsAPI"""
    
    def __init__(self):
        api_key = os.getenv("NEWSAPI_KEY")
        if not api_key:
            print("⚠️ NEWSAPI_KEY manquante dans .env")
            self.client = None
        else:
            self.client = NewsApiClient(api_key=api_key)
            print("✅ NewsAPI initialisé")
    
    def search_articles(self, query: str, max_results: int = 10) -> List[dict]:
        """Recherche d'articles via NewsAPI"""
        if not self.client:
            print("❌ NewsAPI non disponible")
            return []
        
        try:
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            response = self.client.get_everything(
                q=query,
                language='fr',
                from_param=from_date,
                sort_by='relevancy',
                page_size=min(max_results, 100)
            )
            
            articles = []
            for art in response.get('articles', []):
                title = art['title']
                desc = art.get('description') or ''
                
                # Filtre STRICT : le mot-clé doit être dans le titre OU 
                # apparaître au moins 2 fois dans la description
                title_lower = title.lower()
                desc_lower = desc.lower()
                query_lower = query.lower()
                
                in_title = query_lower in title_lower
                count_in_desc = desc_lower.count(query_lower)
                
                # On garde SI :
                # - Le mot est dans le titre (très pertinent)
                # - OU il apparaît 2+ fois dans la description
                if in_title or count_in_desc >= 2:
                    articles.append({
                        'title': art['title'],
                        'url': art['url'],
                        'source': art['source']['name'],
                        'published_at': art['publishedAt'],
                        'description': art.get('description', ''),
                        'content': art.get('content', ''),
                        'author': art.get('author', 'Inconnu'),
                    })
            
            print(f"📰 NewsAPI : {len(articles)} articles trouvés pour '{query}'")
            return articles
            
        except Exception as e:
            print(f"❌ Erreur NewsAPI : {e}")
            return []
