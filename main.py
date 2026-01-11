import asyncio
import sys
import os
from typing import List
from dotenv import load_dotenv

# Ajout du chemin backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

load_dotenv('backend/.env')

from src.services.scraper import RSSScraper
from src.services.email_service import EmailService
from src.database import init_db, SessionLocal
from src.models import Article

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

console = Console()

# 🧠 LA MÉMOIRE DE L'AGENT
LAST_SEARCH_RESULTS = []

def print_banner():
    console.print(Panel.fit(
        "[bold cyan]🤖 NEXUS AGENT v3.0[/bold cyan]\n"
        "[dim]Je cherche, je filtre, j'envoie.[/dim]",
        border_style="cyan"
    ))

def show_help():
    md = """
    **Commandes :**
    - *"Cherche [mot]"* : Trouve des articles précis (ex: "Cherche Trump").
    - *"Envoie mail"* : Envoie ce qu'on vient de trouver.
    - *"Tout scanner"* : Lance la veille complète.
    - *"Stop"* : Quitter.
    """
    console.print(Markdown(md))

def display_articles(articles):
    """Affiche une liste d'articles formatée"""
    if not articles:
        print("Aucun article à afficher")
        return
    
    for i, art in enumerate(articles, 1):
        # Emoji selon sentiment
        emoji = {"positif": "😊", "négatif": "😞", "neutre": "😐"}.get(
            art.sentiment_label.lower() if art.sentiment_label else "neutre", 
            "📰"
        )
        
        # Affichage
        print(f"{i}. {emoji} {art.title}")
        print(f"   📰 {art.source} | 🎭 {art.sentiment_label or 'N/A'}")
        print(f"   🔗 {art.url}")
        if art.summary and art.summary != "Non disponible":
            print(f"   📝 {art.summary[:150]}...")
        print()
        
def run_search(query: str):
    """Recherche des articles par mot-clé"""
    global LAST_SEARCH_RESULTS  # ← DÉPLACER ICI EN PREMIER
    
    if not query:
        print("Veuillez indiquer un mot-clé")
        return
    
    print(f"🕵️‍♂️ Recherche : '{query.upper()}'...")
    
    # 1. Scraper de nouveaux articles
    scraper = RSSScraper(max_articles_per_topic=10)
    new_articles = scraper.scrape_topic("sport", query=query)
    
    # 2. Si aucun nouveau, chercher dans la base
    if not new_articles:
        print("📭 Aucun nouvel article, recherche dans la base...")
        db = SessionLocal()
        
        # Recherche en base avec le mot-clé
        existing_articles = db.query(Article).filter(
            Article.title.contains(query) | Article.content.contains(query)
        ).order_by(Article.created_at.desc()).limit(10).all()
        
        db.close()
        
        if existing_articles:
            print(f"📚 {len(existing_articles)} article(s) trouvé(s) en base\n")
            display_articles(existing_articles)
            LAST_SEARCH_RESULTS = existing_articles  # ← Plus de global ici
            return
        else:
            print(f"Rien trouvé pour '{query}'.")
            return
    
    # 3. Afficher les nouveaux articles
    print(f"\n🆕 {len(new_articles)} nouvel(aux) article(s)\n")
    display_articles(new_articles)
    
    LAST_SEARCH_RESULTS = new_articles  # ← Plus de global ici

def send_email_smart():
    global LAST_SEARCH_RESULTS
    email_service = EmailService()
    
    # ON RÉCUPÈRE L'EMAIL DEPUIS LA CONFIGURATION (plus pro !)
    user_email = os.getenv("USER_EMAIL")
    
    # Sécurité : Si le prof a oublié de mettre son email dans le .env
    if not user_email:
        console.print("[red]❌ Erreur : Aucune adresse email trouvée dans le fichier .env[/red]")
        console.print("[dim]Ajoutez la ligne : USER_EMAIL=votre@email.com dans le fichier .env[/dim]")
        return

    destinataires = [user_email]

    if LAST_SEARCH_RESULTS:
        console.print(f"[bold blue]📧 Envoi des {len(LAST_SEARCH_RESULTS)} articles à {user_email}...[/bold blue]")
        email_service.send_daily_newsletter(destinataires=destinataires, specific_articles=LAST_SEARCH_RESULTS)
        console.print("[green]✅ Mail envoyé ![/green]")
    else:
        console.print("[yellow]Pas de recherche en mémoire.[/yellow]")
        if Prompt.ask("Envoyer tout le stock ?", choices=["y", "n"]) == "y":
            email_service.send_daily_newsletter(destinataires=destinataires)
            console.print("[green]✅ Mail global envoyé ![/green]")


            
def run_full_cycle():
    global LAST_SEARCH_RESULTS
    console.print("[bold magenta]🚀 Cycle complet...[/bold magenta]")
    scraper = RSSScraper(max_articles_per_topic=10)
    topics = ["économie", "climat", "politique", "géopolitique", "sport"]
    all_articles = []
    
    for topic in topics:
        console.print(f"   📡 {topic}...")
        arts = scraper.scrape_topic(topic)
        all_articles.extend(arts)
    
    LAST_SEARCH_RESULTS = all_articles
    console.print(f"[green]✅ {len(all_articles)} articles récupérés.[/green]")

def main():
    print_banner()
    init_db()
    
    while True:
        console.print("\n[bold cyan]Nexus >[/bold cyan] ", end="")
        user_input = input().lower()

        if user_input in ["exit", "stop", "quitter"]:
            break
        elif "aide" in user_input:
            show_help()
        elif "cherche" in user_input:
            words = user_input.split()
            if len(words) > 1:
                run_search(words[1])
            else:
                q = Prompt.ask("Quel mot-clé ?")
                run_search(q)
        elif "mail" in user_input or "envoie" in user_input:
            send_email_smart()
        elif "tout" in user_input:
            run_full_cycle()
        else:
            console.print("[red]?[/red] Tapez 'aide'.")

if __name__ == "__main__":
    main()