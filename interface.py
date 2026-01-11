import sys
import os
from datetime import datetime
from typing import List

# Ajout du chemin backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import gradio as gr
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv

from src.services.scraper import RSSScraper
from src.services.email_service import EmailService
from src.services.subscription_service import SubscriptionService
from src.database import SessionLocal, init_db
from src.models import Article

# Charger les variables d'environnement
load_dotenv('backend/.env')

# Initialiser la base de données
init_db()

# Variables globales
LAST_SEARCH_RESULTS = []

# ═══════════════════════════════════════════════════════════════
# FONCTIONS BACKEND
# ═══════════════════════════════════════════════════════════════

def search_articles(query: str) -> str:
    """Recherche d'articles avec mot-clé"""
    global LAST_SEARCH_RESULTS
    
    if not query or len(query.strip()) < 2:
        return "⚠️ Veuillez entrer un mot-clé (minimum 2 caractères)"
    
    try:
        scraper = RSSScraper(max_articles_per_topic=10)
        articles = scraper.scrape_topic("sport", query=query.strip())
        
        LAST_SEARCH_RESULTS = articles
        
        if not articles:
            return f"❌ Aucun article trouvé pour '{query}'"
        
        # Formatage des résultats
        result = f"✅ **{len(articles)} articles trouvés pour '{query}'**\n\n"
        
        for i, art in enumerate(articles, 1):
            emoji = {"positif": "😊", "négatif": "😞", "neutre": "😐"}.get(art.sentiment_label.lower(), "📰")
            color = {"positif": "🟢", "négatif": "🔴", "neutre": "🟡"}.get(art.sentiment_label.lower(), "⚪")
            
            result += f"**{i}. {emoji} {art.title}**\n"
            result += f"   {color} Sentiment: **{art.sentiment_label.upper()}**\n"
            result += f"   📰 Source: {art.source}\n"
            result += f"   🔗 [Lire l'article]({art.url})\n\n"
        
        result += f"💡 *Tapez sur 'Envoyer Email' pour envoyer ces articles à tous les abonnés*"
        
        return result
        
    except Exception as e:
        return f"❌ Erreur lors de la recherche : {str(e)}"

def send_newsletter() -> str:
    """Envoie la newsletter à TOUS les abonnés actifs"""
    global LAST_SEARCH_RESULTS
    
    try:
        # Récupérer tous les abonnés actifs
        sub_service = SubscriptionService()
        subscribers = sub_service.get_active_subscribers()
        
        if not subscribers:
            return "❌ Aucun abonné dans la base de données\n\n💡 Allez dans l'onglet '✉️ S'abonner' pour ajouter des abonnés."
        
        # Préparer les articles
        if LAST_SEARCH_RESULTS:
            articles = LAST_SEARCH_RESULTS
        else:
            db = SessionLocal()
            articles = db.query(Article).order_by(Article.created_at.desc()).limit(10).all()
            db.close()
        
        if not articles:
            return "❌ Aucun article disponible à envoyer"
        
        # Envoyer à tous les abonnés
        email_service = EmailService()
        destinataires = [sub.email for sub in subscribers]
        
        email_service.send_daily_newsletter(
            destinataires=destinataires,
            specific_articles=articles
        )
        
        return f"""✅ **Newsletter envoyée avec succès !**

📧 **{len(destinataires)} abonné(s)** ont reçu l'email
📰 **{len(articles)} articles** inclus

**Abonnés qui ont reçu la newsletter :**
""" + "\n".join([f"   ✉️ {sub.email}" for sub in subscribers])
        
    except Exception as e:
        return f"❌ Erreur lors de l'envoi : {str(e)}"

def get_latest_articles(limit: int = 10) -> str:
    """Récupère les derniers articles stockés"""
    try:
        db = SessionLocal()
        articles = db.query(Article).order_by(Article.created_at.desc()).limit(limit).all()
        db.close()
        
        if not articles:
            return "📭 Aucun article en base de données\nFaites une recherche pour commencer !"
        
        result = f"📰 **{len(articles)} derniers articles**\n\n"
        
        for i, art in enumerate(articles, 1):
            emoji = {"positif": "😊", "négatif": "😞", "neutre": "😐"}.get(art.sentiment_label.lower(), "📰")
            color = {"positif": "🟢", "négatif": "🔴", "neutre": "🟡"}.get(art.sentiment_label.lower(), "⚪")
            
            result += f"**{i}. {emoji} {art.title[:80]}...**\n"
            result += f"   {color} {art.sentiment_label.upper()} | 📰 {art.source} | 📅 {art.created_at.strftime('%d/%m %H:%M')}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ Erreur : {str(e)}"

def get_statistics() -> tuple:
    """Génère les statistiques et graphiques"""
    try:
        db = SessionLocal()
        articles = db.query(Article).all()
        db.close()
        
        if not articles:
            return "📊 Aucune donnée disponible", None, None
        
        # Stats textuelles
        total = len(articles)
        sentiments = {}
        sources = {}
        
        for art in articles:
            sent = art.sentiment_label.lower()
            sentiments[sent] = sentiments.get(sent, 0) + 1
            sources[art.source] = sources.get(art.source, 0) + 1
        
        stats_text = f"📊 **STATISTIQUES NEXUS**\n\n"
        stats_text += f"📰 Total articles : **{total}**\n\n"
        stats_text += f"**Répartition des sentiments :**\n"
        stats_text += f"😊 Positif : {sentiments.get('positif', 0)} ({sentiments.get('positif', 0)/total*100:.1f}%)\n"
        stats_text += f"😐 Neutre : {sentiments.get('neutre', 0)} ({sentiments.get('neutre', 0)/total*100:.1f}%)\n"
        stats_text += f"😞 Négatif : {sentiments.get('négatif', 0)} ({sentiments.get('négatif', 0)/total*100:.1f}%)\n\n"
        stats_text += f"**Top 5 sources :**\n"
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]:
            stats_text += f"📰 {source} : {count} articles\n"
        
        # Graphique sentiments (Pie chart)
        fig_sentiment = go.Figure(data=[go.Pie(
            labels=['😊 Positif', '😐 Neutre', '😞 Négatif'],
            values=[sentiments.get('positif', 0), sentiments.get('neutre', 0), sentiments.get('négatif', 0)],
            marker=dict(colors=['#10b981', '#f59e0b', '#ef4444']),
            hole=0.4
        )])
        fig_sentiment.update_layout(
            title="Répartition des Sentiments",
            height=400
        )
        
        # Graphique sources (Bar chart)
        top_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]
        fig_sources = go.Figure(data=[go.Bar(
            x=[s[0] for s in top_sources],
            y=[s[1] for s in top_sources],
            marker_color='#2563eb'
        )])
        fig_sources.update_layout(
            title="Top 10 Sources",
            xaxis_title="Source",
            yaxis_title="Nombre d'articles",
            height=400
        )
        
        return stats_text, fig_sentiment, fig_sources
        
    except Exception as e:
        return f"❌ Erreur : {str(e)}", None, None

def subscribe_newsletter(email: str) -> str:
    """S'abonner à la newsletter avec email de confirmation"""
    if not email or "@" not in email:
        return "❌ Veuillez entrer une adresse email valide"
    
    try:
        sub_service = SubscriptionService()
        result = sub_service.subscribe(email)
        
        if result["success"]:
            return f"""✅ **Abonnement confirmé !**

📧 Email enregistré : `{email}`

🎉 Un **email de bienvenue** a été envoyé à cette adresse.

💡 **Ce qui va se passer :**
- Email de confirmation envoyé immédiatement
- Newsletters envoyées automatiquement tous les matins à 7h
- Sélection des meilleurs articles par Gemini AI

🔧 **Pour tester maintenant :**
1. Allez dans l'onglet '🔍 Recherche'
2. Cherchez des articles
3. Puis '📧 Envoyer Email' pour envoyer à tous les abonnés"""
        else:
            return result["message"]
    
    except Exception as e:
        return f"❌ Erreur lors de l'abonnement : {str(e)}"

def get_subscribers_list() -> str:
    """Afficher la liste des abonnés"""
    try:
        sub_service = SubscriptionService()
        subscribers = sub_service.get_active_subscribers()
        
        if not subscribers:
            return "📭 Aucun abonné pour le moment"
        
        result = f"👥 **{len(subscribers)} abonné(s) actif(s)**\n\n"
        
        for i, sub in enumerate(subscribers, 1):
            result += f"{i}. 📧 {sub.email}\n"
            result += f"   📅 Abonné depuis : {sub.subscribed_at.strftime('%d/%m/%Y %H:%M')}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ Erreur : {str(e)}"

# ═══════════════════════════════════════════════════════════════
# INTERFACE GRADIO
# ═══════════════════════════════════════════════════════════════

def create_interface():
    """Crée l'interface Gradio"""
    
    with gr.Blocks(
        theme=gr.themes.Soft(primary_hue="blue"),
        title="Nexus - Interface Graphique"
    ) as interface:
        
        # Header
        gr.Markdown("""
        # 🤖 NEXUS - Interface Graphique
        ### Votre système de veille intelligente avec IA et abonnements
        """)
        
        # Tabs principales
        with gr.Tabs():
            
            # ═══════════════════════════════════════════════════════════════
            # TAB 1 : RECHERCHE
            # ═══════════════════════════════════════════════════════════════
            with gr.Tab("🔍 Recherche"):
                gr.Markdown("### Rechercher des articles par mot-clé")
                
                with gr.Row():
                    search_input = gr.Textbox(
                        label="Mot-clé",
                        placeholder="Ex: tennis, football, Macron...",
                        scale=3
                    )
                    search_btn = gr.Button("🔍 Chercher", variant="primary", scale=1)
                
                search_output = gr.Markdown(label="Résultats")
                
                search_btn.click(
                    fn=search_articles,
                    inputs=search_input,
                    outputs=search_output
                )
            
            # ═══════════════════════════════════════════════════════════════
            # TAB 2 : DERNIERS ARTICLES
            # ═══════════════════════════════════════════════════════════════
            with gr.Tab("📰 Derniers Articles"):
                gr.Markdown("### Articles récemment collectés")
                
                with gr.Row():
                    limit_slider = gr.Slider(
                        minimum=5,
                        maximum=50,
                        value=10,
                        step=5,
                        label="Nombre d'articles à afficher"
                    )
                    refresh_btn = gr.Button("🔄 Rafraîchir", variant="secondary")
                
                latest_output = gr.Markdown()
                
                # Charger au démarrage
                interface.load(
                    fn=lambda: get_latest_articles(10),
                    outputs=latest_output
                )
                
                refresh_btn.click(
                    fn=get_latest_articles,
                    inputs=limit_slider,
                    outputs=latest_output
                )
            
            # ═══════════════════════════════════════════════════════════════
            # TAB 3 : S'ABONNER
            # ═══════════════════════════════════════════════════════════════
            with gr.Tab("✉️ S'abonner"):
                gr.Markdown("""
                ### S'abonner à la newsletter Nexus
                
                Recevez automatiquement les meilleurs articles sélectionnés par Gemini AI.
                
                🎯 **Fonctionnalités :**
                - Email de confirmation immédiat
                - Newsletter quotidienne à 7h du matin
                - Articles analysés par IA (sentiment + résumé)
                - Sélection intelligente des actualités importantes
                """)
                
                with gr.Row():
                    subscribe_email = gr.Textbox(
                        label="Adresse email",
                        placeholder="exemple@email.com",
                        scale=3
                    )
                    subscribe_btn = gr.Button("✉️ S'abonner", variant="primary", scale=1)
                
                subscribe_output = gr.Markdown()
                
                subscribe_btn.click(
                    fn=subscribe_newsletter,
                    inputs=subscribe_email,
                    outputs=subscribe_output
                )
                
                gr.Markdown("---")
                
                gr.Markdown("### 👥 Liste des abonnés")
                
                list_btn = gr.Button("📋 Afficher les abonnés", variant="secondary")
                list_output = gr.Markdown()
                
                list_btn.click(
                    fn=get_subscribers_list,
                    outputs=list_output
                )
            
            # ═══════════════════════════════════════════════════════════════
            # TAB 4 : ENVOYER EMAIL
            # ═══════════════════════════════════════════════════════════════
            with gr.Tab("📧 Envoyer Email"):
                gr.Markdown("""
                ### Envoyer la newsletter à tous les abonnés
                
                Cette fonction envoie la newsletter à **TOUS** les abonnés actifs.
                
                📋 **Contenu envoyé :**
                - Si vous venez de faire une recherche : les articles trouvés
                - Sinon : les 10 derniers articles de la base de données
                """)
                
                send_btn = gr.Button("📧 Envoyer la Newsletter à tous les abonnés", variant="primary", size="lg")
                send_output = gr.Markdown()
                
                send_btn.click(
                    fn=send_newsletter,
                    outputs=send_output
                )
            
            # ═══════════════════════════════════════════════════════════════
            # TAB 5 : STATISTIQUES
            # ═══════════════════════════════════════════════════════════════
            with gr.Tab("📊 Statistiques"):
                gr.Markdown("### Analyse des données collectées")
                
                stats_btn = gr.Button("📊 Générer les Statistiques", variant="primary")
                
                with gr.Row():
                    stats_text = gr.Markdown()
                
                with gr.Row():
                    with gr.Column():
                        sentiment_chart = gr.Plot(label="Répartition Sentiments")
                    with gr.Column():
                        sources_chart = gr.Plot(label="Top Sources")
                
                stats_btn.click(
                    fn=get_statistics,
                    outputs=[stats_text, sentiment_chart, sources_chart]
                )
        
        # Footer
        gr.Markdown("""
        ---
        💡 **Astuces :**
        - Abonnez-vous (et vos amis) pour recevoir les newsletters automatiquement
        - Les articles sont analysés avec BERT (sentiment) et Gemini AI (importance)
        - Les newsletters sont envoyées tous les matins à 7h via GitHub Actions
        
        🔧 **Powered by** NewsAPI + Gemini AI + BERT + Transformers + Resend
        """)
    
    return interface

# ═══════════════════════════════════════════════════════════════
# LANCEMENT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🚀 Lancement de l'interface Nexus...")
    print(f"🔑 NewsAPI : {'✅ Configuré' if os.getenv('NEWSAPI_KEY') else '❌ Non configuré'}")
    print(f"📨 Resend : {'✅ Configuré' if os.getenv('RESEND_API_KEY') else '❌ Non configuré'}")
    print(f"🤖 Gemini : {'✅ Configuré' if os.getenv('GEMINI_API_KEY') else '❌ Non configuré'}")
    print("\n🌐 Ouverture dans votre navigateur...")
    
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )