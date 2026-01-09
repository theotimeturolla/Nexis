import asyncio
import sys
import os
from typing import List

# On ajoute le dossier backend au chemin
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from src.services.scraper import RSSScraper
from src.services.email_service import EmailService
# Note : Assurez-vous d'avoir bien ajouté init_db dans src/database.py comme vu précédemment
from src.database import init_db, SessionLocal
from src.models import Article

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

console = Console()

def print_banner():
    console.print(Panel.fit(
        "[bold cyan]🤖 NEXUS AGENT v2.0 (Recherche Active)[/bold cyan]\n"
        "[dim]Je suis prêt à filtrer l'actualité pour vous.[/dim]",
        border_style="cyan"
    ))

def show_help():
    md = """
    **Commandes disponibles :**
    - *"Je veux faire une recherche"* : Cherche un mot précis (ex: Trump, IA, Climat).
    - *"Lance tout"* : Scrape tous les sujets et envoie la newsletter.
    - *"Donne moi les news sport"* : Scrape uniquement le sport.
    - *"Quitter"* : Arrête l'agent.
    """
    console.print(Markdown(md))

def run_specific_topic(topic: str):
    """Outil : Scrape un seul sujet"""
    console.print(f"[bold yellow]🔍 Analyse du sujet : {topic.upper()}...[/bold yellow]")
    scraper = RSSScraper()
    articles = scraper.scrape_topic(topic)
    if not articles:
        console.print(f"[red]Aucun nouvel article trouvé pour {topic}.[/red]")
        return
    console.print(f"[green]✅ {len(articles)} articles trouvés ![/green]")
    for art in articles:
        console.print(f"- [bold]{art.title}[/bold] ({art.source})")

def run_search(query: str):
    """Outil : Cherche un mot-clé dans TOUS les sujets"""
    console.print(f"[bold yellow]🕵️‍♂️ Recherche d'actualités sur : '{query.upper()}'...[/bold yellow]")
    
    scraper = RSSScraper(max_articles_per_topic=5)
    topics = ["économie", "climat", "politique", "géopolitique", "sport"]
    total_found = 0
    
    for topic in topics:
        # On utilise le nouveau paramètre 'query'
        articles = scraper.scrape_topic(topic, query=query)
        if articles:
            console.print(f"   [cyan]{topic.capitalize()}[/cyan] : {len(articles)} article(s)")
            for art in articles:
                console.print(f"   - {art.title} [dim]({art.source})[/dim]")
            total_found += len(articles)
            
    if total_found == 0:
        console.print(f"[red]Aucun article trouvé parlant de '{query}'.[/red]")
    else:
        console.print(f"[green]✅ Terminé. {total_found} articles trouvés sur '{query}'.[/green]")

def run_full_cycle():
    """Outil : Tout scraper et envoyer l'email"""
    console.print("[bold magenta]🚀 Lancement du cycle complet...[/bold magenta]")
    init_db()
    scraper = RSSScraper(max_articles_per_topic=10)
    email_service = EmailService()
    topics = ["économie", "climat", "politique", "géopolitique", "sport"]
    total_articles = 0
    for topic in topics:
        console.print(f"   📡 Scan de : {topic}...")
        articles = scraper.scrape_topic(topic)
        total_articles += len(articles)
    
    if total_articles > 0:
        console.print("   📧 Envoi de l'email...")
        email_service.send_daily_newsletter(destinataires=["juleschopard11@gmail.com"])
        console.print("[bold green]✅ Fini ![/bold green]")
    else:
        console.print("[yellow]Pas assez de nouveautés.[/yellow]")

def main():
    print_banner()
    while True:
        console.print("\n[bold cyan]Que voulez-vous faire ?[/bold cyan]")
        user_input = Prompt.ask("[dim](Tapez 'aide' pour les options)[/dim] >").lower()

        if user_input in ["exit", "quit", "quitter", "stop"]:
            console.print("[red]Arrêt du système. 👋[/red]")
            break
        elif "aide" in user_input:
            show_help()
        
        # 👇 NOUVEAU : La commande Recherche
        elif "cherche" in user_input or "recherche" in user_input or "trouve" in user_input:
            search_term = Prompt.ask("[bold yellow]Quel mot-clé voulez-vous chercher ?[/bold yellow] (ex: Trump, Mbappe)")
            run_search(search_term)

        elif "tout" in user_input or "complet" in user_input:
            run_full_cycle()
        elif "sport" in user_input:
            run_specific_topic("sport")
        elif "eco" in user_input:
            run_specific_topic("économie")
        elif "pol" in user_input:
            run_specific_topic("politique")
        elif "climat" in user_input:
            run_specific_topic("climat")
        elif "géo" in user_input:
            run_specific_topic("géopolitique")
        else:
            console.print("[bold red]❌ Je n'ai pas compris.[/bold red]")
            console.print("Essayez : 'Je veux faire une recherche' ou 'aide'.")

if __name__ == "__main__":
    init_db()
    main()