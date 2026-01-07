import sys
import os

# --- HACK POUR LES IMPORTS ---
# Permet de lancer le script depuis n'importe où sans erreur "ModuleNotFound"
current_dir = os.path.dirname(os.path.abspath(__file__)) # backend/src/services
backend_dir = os.path.dirname(os.path.dirname(current_dir)) # backend
if backend_dir not in sys.path:
    sys.path.append(backend_dir)
# -----------------------------

import requests
import feedparser
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime
import logging

# Imports Interface
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich import box
from rich.align import Align

# Imports IA & Base de données
from src.services.sentiment_analyzer import SentimentAnalyzer
from src.services.llm_processor import LLMProcessor
from src.database import SessionLocal
from src.models import Article

logger = logging.getLogger(__name__)

# ============================================================
#                      SCRAPER INTELLIGENT
# ============================================================

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
    }

    def __init__(self, max_articles_per_topic: int = 3):
        self.max_articles_per_topic = max_articles_per_topic
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "BotActu/1.0"})
        
        # Initialisation des cerveaux
        self.analyzer = SentimentAnalyzer()
        self.llm_processor = LLMProcessor()
        
        # Connexion à la base de données
        self.db = SessionLocal()

    def fetch_article_text(self, url: str) -> str:
        try:
            r = self.session.get(url, timeout=4)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            tags = ["article", "main", "div.content", "div.post-content", "div#content"]
            for t in tags:
                content = soup.select_one(t)
                if content:
                    return content.get_text(" ", strip=True)
            return ""
        except Exception:
            return ""

    def article_exists(self, url: str) -> bool:
        """Vérifie si l'URL est déjà dans la base de données."""
        return self.db.query(Article).filter(Article.url == url).first() is not None

    def save_to_db(self, article_data: dict):
        """Sauvegarde un nouvel article dans la base."""
        try:
            new_article = Article(**article_data)
            self.db.add(new_article)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Erreur sauvegarde DB: {e}")
            self.db.rollback()
            return False

    def scrape_topic(self, topic: str) -> List[Article]:
        new_articles_found = []
        feeds = self.RSS_FEEDS.get(topic, {})
        
        for feed_name, feed_url in feeds.items():
            feed = feedparser.parse(feed_url)
            if feed.bozo: continue

            for entry in feed.entries:
                if len(new_articles_found) >= self.max_articles_per_topic: break
                
                link = entry.link
                title = entry.title

                # 1. LE FILTRE MÉMOIRE : On vérifie si on connait déjà
                if self.article_exists(link):
                    # On l'ignore silencieusement
                    continue

                # Si on est ici, c'est un NOUVEL article !
                try:
                    # A. Téléchargement
                    full_text = self.fetch_article_text(link)
                    text_to_analyze = full_text if len(full_text) > 100 else f"{title} {entry.get('description', '')}"
                    
                    # B. Analyse Sentiment (Cœur)
                    sentiment_score, sentiment_label = self.analyzer.analyze(text_to_analyze)

                    # C. Analyse IA (Cerveau)
                    ai_summary = "Non disponible"
                    reliability = 50
                    source_count = 0
                    
                    if len(full_text) > 300:
                        analysis = self.llm_processor.analyze_content(full_text)
                        if analysis:
                            ai_summary = analysis.summary
                            reliability = analysis.reliability_score
                            source_count = len(analysis.sources)

                    # D. Préparation des données pour la sauvegarde
                    article_data = {
                        "title": title,
                        "url": link,
                        "source": feed_name,
                        "topic": topic,
                        "published_date": datetime.now(), # Idéalement parser entry.published_parsed
                        "content": full_text[:5000], # On garde un extrait
                        "sentiment_score": sentiment_score,
                        "sentiment_label": sentiment_label,
                        "summary": ai_summary,
                        "reliability_score": reliability,
                        "source_count": source_count
                    }

                    # E. Sauvegarde dans la mémoire
                    self.save_to_db(article_data)
                    
                    # On l'ajoute à la liste pour l'affichage
                    # (On crée un objet Article temporaire pour l'affichage Rich)
                    display_obj = Article(**article_data)
                    new_articles_found.append(display_obj)
                    
                except Exception as e:
                    logger.error(f"Erreur traitement {link}: {e}")
                    continue
                    
        return new_articles_found

# ============================================================
#                        LANCEMENT
# ============================================================

if __name__ == "__main__":
    console = Console()
    scraper = RSSScraper(max_articles_per_topic=2) # On réduit un peu pour tester vite
    topics = ["économie", "climat", "politique", "géopolitique"]

    console.print(Panel(Align.center("[bold white]🧠 NEXUS : SCRAPER + MÉMOIRE[/]"), border_style="green"))

    results = {}
    with Progress(
        SpinnerColumn(style="green"),
        TextColumn("[bold green]{task.description}"),
        BarColumn(style="green"),
        TaskProgressColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Lecture des news...", total=len(topics))
        for topic in topics:
            progress.update(task, description=f"Analyse : [bold]{topic.upper()}[/] (Seulement les nouveaux)")
            results[topic] = scraper.scrape_topic(topic)
            progress.advance(task)

    # Affichage des résultats
    console.print("\n")
    total_new = 0
    
    for topic, items in results.items():
        if not items: continue
        total_new += len(items)

        table = Table(title=f"Nouveautés : [bold cyan]{topic.upper()}[/]", box=box.ROUNDED)
        table.add_column("Humeur", justify="center")
        table.add_column("Titre & Résumé IA")
        table.add_column("Fiabilité")

        for a in items:
            mood_icon = "🟢" if a.sentiment_label == "positif" else "🔴" if a.sentiment_label == "négatif" else "⚪"
            
            table.add_row(
                f"{mood_icon}\n{a.sentiment_score:.2f}",
                f"[bold]{a.title}[/]\n[dim]{a.summary[:150]}...[/]",
                f"🛡️ {a.reliability_score}/100"
            )
        console.print(table)
        console.print("\n")

    if total_new == 0:
        console.print("[bold yellow]Aucun nouvel article trouvé.[/] (Tout est déjà en mémoire !)")
    else:
        console.print(f"[bold green]{total_new} nouveaux articles sauvegardés en base ![/]")