import requests
import feedparser
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

# Imports pour l'interface
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich import box
from rich.text import Text
from rich.align import Align

logger = logging.getLogger(__name__)

# ============================================================
#                 STRUCTURE DES DONNÉES (INCHANGÉ)
# ============================================================

class ArticleData:
    """Structure de données pour un article."""
    
    def __init__(
        self,
        title: str,
        url: str,
        source: str,
        topic: str,
        published_date: Optional[datetime] = None,
        text: Optional[str] = None,
        authors: Optional[List[str]] = None,
    ):
        self.title = title
        self.url = url
        self.source = source
        self.topic = topic
        self.published_date = published_date or datetime.now()
        self.text = text or ""
        self.authors = authors or []
        self.scraped_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "topic": self.topic,
            "published_date": self.published_date.isoformat(),
            "text": self.text,
            "authors": self.authors,
            "scraped_at": self.scraped_at.isoformat(),
        }


# ============================================================
#                      SCRAPER RSS (INCHANGÉ)
# ============================================================

class RSSScraper:
    
    RSS_FEEDS = {
        "économie": {
            "lesechos": "https://news.google.com/rss/search?q=site:lesechos.fr+économie&hl=fr&gl=FR&ceid=FR:fr",
            "latribune": "https://news.google.com/rss/search?q=site:latribune.fr+économie&hl=fr&gl=FR&ceid=FR:fr",
            "challenges": "https://news.google.com/rss/search?q=site:challenges.fr+économie&hl=fr&gl=FR&ceid=FR:fr"
        },
        "climat": {
            "lemonde_planete": "https://www.lemonde.fr/planete/rss_full.xml",
            "reporterre": "https://reporterre.net/spip.php?page=backend",
            "liberation_env": "https://www.liberation.fr/arc/outboundfeeds/rss/category/environnement/"
        },
        "politique française": {
            "lemonde_pol": "https://www.lemonde.fr/politique/rss_full.xml",
            "liberation_pol": "https://www.liberation.fr/arc/outboundfeeds/rss/category/politique/",
            "lefigaro_pol": "https://www.lefigaro.fr/rss/figaro_politique.xml",
        },
        "géopolitique": {
            "lemonde_inter": "https://www.lemonde.fr/international/rss_full.xml",
            "courrierinter": "https://www.courrierinternational.com/feed/all/rss.xml",
            "diploweb": "https://www.diploweb.com/spip.php?page=backend",
        },
    }

    def __init__(self, max_articles_per_topic: int = 5):
        self.max_articles_per_topic = max_articles_per_topic
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0"
        })

    def fetch_article_text(self, url: str) -> str:
        try:
            r = self.session.get(url, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            article_tag = (
                soup.find("article")
                or soup.find("div", class_="article__content")
                or soup.find("div", class_="content")
                or soup.find("div", {"id": "content"})
            )
            if article_tag:
                return article_tag.get_text(" ", strip=True)
            return ""
        except Exception as e:
            logger.error(f"Impossible d'extraire le texte de {url}: {e}")
            return ""

    def scrape_feed(self, feed_name: str, feed_url: str, topic: str) -> List[ArticleData]:
        # logger.info(...) -> Commenté pour garder l'interface propre
        articles = []
        feed = feedparser.parse(feed_url)
        if feed.bozo:
            return articles

        for entry in feed.entries[: self.max_articles_per_topic]:
            try:
                title = entry.title
                link = entry.link
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                
                # Note: fetch_article_text peut être lent, ce qui ralentit l'UI
                text = self.fetch_article_text(link)
                authors = [entry.author] if "author" in entry else []

                articles.append(ArticleData(title, link, feed_name, topic, published, text, authors))
            except Exception:
                pass
        return articles

    def scrape_topic(self, topic: str) -> List[ArticleData]:
        topic_feeds = self.RSS_FEEDS.get(topic, {})
        collected = []
        for feed_name, feed_url in topic_feeds.items():
            collected.extend(self.scrape_feed(feed_name, feed_url, topic))
        return collected[: self.max_articles_per_topic]

    def scrape_all_topics(self, topics: List[str]) -> Dict[str, List[ArticleData]]:
        results = {}
        for topic in topics:
            results[topic] = self.scrape_topic(topic)
        return results


# ============================================================
#              INTERFACE UTILISATEUR (RICH UI)
# ============================================================

if __name__ == "__main__":
    # On met le logging en WARNING ou ERROR pour ne pas polluer l'interface visuelle
    logging.basicConfig(level=logging.ERROR)
    
    console = Console()
    
    # Configuration
    scraper = RSSScraper(max_articles_per_topic=3)
    topics = ["économie", "climat", "politique française", "géopolitique"]

    # --- 1. En-tête (Header) ---
    header_text = Text("🗞️  AGRÉGATEUR RSS INTELLIGENT", style="bold white")
    console.print(Panel(
        Align.center(header_text),
        border_style="blue",
        padding=(1, 2)
    ))

    # --- 2. Scraping avec barre de progression ---
    results = {}
    
    # Utilisation d'une barre de progression plus détaillée
    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=None, style="blue", complete_style="green"),
        TaskProgressColumn(),
        console=console,
        transient=True # Disparaît à la fin pour laisser place aux résultats
    ) as progress:
        
        main_task = progress.add_task("Analyse des flux...", total=len(topics))
        
        for topic in topics:
            progress.update(main_task, description=f"Scraping : [bold]{topic.upper()}[/]")
            
            # On appelle scrape_topic directement ici pour mettre à jour la barre
            # au fur et à mesure, plutôt que tout attendre d'un coup.
            topic_results = scraper.scrape_topic(topic)
            results[topic] = topic_results
            
            progress.advance(main_task)

    # --- 3. Affichage des résultats (Tables) ---
    console.print("\n") # Petit espace après le chargement

    total_articles = sum(len(items) for items in results.values())
    
    if total_articles == 0:
        console.print(Panel("Aucun article trouvé. Vérifiez votre connexion.", style="red"))
    else:
        for topic, items in results.items():
            if not items:
                continue

            # Création du tableau principal pour la catégorie
            table = Table(
                title=f"CATEGORY : [bold underline cyan]{topic.upper()}[/]",
                title_justify="left",
                box=box.ROUNDED,      # Bords arrondis modernes
                expand=True,          # Prend toute la largeur du terminal
                header_style="bold white on blue",
                border_style="bright_black",
                show_lines=True,      # Ligne de séparation entre chaque article
                padding=(0, 1)
            )

            # --- Définition des colonnes intelligentes ---
            # Colonne 1 : Métadonnées (Source + Date) combinées pour gagner de la place
            table.add_column("Source & Date", justify="right", style="dim", width=18)
            
            # Colonne 2 : Le Titre (prend le plus de place)
            table.add_column("Titre de l'article", style="white", ratio=4, overflow="fold")
            
            # Colonne 3 : Le Lien (cliquable)
            table.add_column("Lien", style="blue", justify="center", width=10)

            for a in items:
                # Formatage date
                date_str = "Récent"
                if a.published_date:
                    date_str = a.published_date.strftime("%d/%m %H:%M")
                
                # Formatage métadonnées (Source en gras vert, Date en dessous)
                meta_info = f"[bold green]{a.source}[/]\n{date_str}"
                
                # Lien cliquable avec texte court
                link_btn = f"[link={a.url}][bold blue]Ouvrir ↗[/][/link]"

                table.add_row(
                    meta_info,
                    a.title,
                    link_btn
                )

            console.print(table)
            console.print("\n") # Espace entre les tableaux

    # --- Footer ---
    console.print(f"[dim italic right]Fin du rapport • {total_articles} articles extraits • {datetime.now().strftime('%H:%M:%S')}[/dim italic right]")