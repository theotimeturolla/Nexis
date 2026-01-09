import asyncio
import sys
import os
from typing import List

# Ajout du chemin backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

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

def run_search(query: str):
    global LAST_SEARCH_RESULTS
    
    console.print(f"[bold yellow]🕵️‍♂️ Recherche : '{query.upper()}'...[/bold yellow]")
    
    scraper = RSSScraper(max_articles_per_topic=5)
    topics = ["économie", "climat", "politique", "géopolitique", "sport"]
    found_articles = []
    
    for topic in topics:
        articles = scraper.scrape_topic(topic, query=query)
        if articles:
            console.print(f"   [cyan]{topic.capitalize()}[/cyan] : {len(articles)} trouvé(s)")
            for art in articles:
                console.print(f"   - {art.title}")
            found_articles.extend(articles)
            
    if not found_articles:
        console.print(f"[red]Rien trouvé pour '{query}'.[/red]")
        LAST_SEARCH_RESULTS = []
    else:
        console.print(f"[green]✅ {len(found_articles)} articles en mémoire ![/green]")
        console.print("[dim]Tapez 'envoie mail' pour les recevoir.[/dim]")
        LAST_SEARCH_RESULTS = found_articles

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