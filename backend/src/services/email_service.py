import os
import resend
from typing import List
from dotenv import load_dotenv
from src.database import SessionLocal
from src.models import Article

load_dotenv()

class EmailService:
    def __init__(self):
        api_key = os.getenv("RESEND_API_KEY")
        if not api_key:
            print("⚠️ ATTENTION : Pas de clé API Resend trouvée dans le .env")
        resend.api_key = api_key
        self.db = SessionLocal()

    def generate_html(self, articles: List[Article]) -> str:
        items_html = ""
        for art in articles:
            color = "#10b981" if art.sentiment_label == "POSITIF" else "#ef4444"
            items_html += f"""
            <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid {color}; background: #f9f9f9;">
                <h3 style="margin: 0; color: #333;">{art.title}</h3>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">
                    Source: {art.source} | Sujet: {art.topic.upper()}
                </p>
                <p style="color: #444;">{art.summary}</p>
                <a href="{art.url}" style="color: {color}; text-decoration: none; font-weight: bold;">Lire la suite →</a>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">
                🤖 Nexus : Votre Revue de Presse
            </h1>
            <p>Voici les articles sélectionnés pour vous :</p>
            {items_html}
            <p style="font-size: 12px; color: #888; margin-top: 30px;">Généré par Nexus AI Agent</p>
        </body>
        </html>
        """

    def send_daily_newsletter(self, destinataires: List[str], specific_articles: List[Article] = None):
        # SI on a une liste spécifique (suite à une recherche), on prend ça
        if specific_articles:
            articles = specific_articles
            print(f"📧 Préparation de l'envoi de {len(articles)} articles ciblés...")
        # SINON, on prend les derniers en base
        else:
            print("📧 Récupération des derniers articles en base...")
            articles = self.db.query(Article).order_by(Article.created_at.desc()).limit(50).all()

        if not articles:
            print("❌ Aucun article à envoyer.")
            return

        html_content = self.generate_html(articles)

        try:
            r = resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": destinataires,
                "subject": f"📢 Nexus : {len(articles)} Nouveaux Articles",
                "html": html_content
            })
            print(f"✅ Email envoyé ! ID: {r.get('id')}")
        except Exception as e:
            print(f"❌ Erreur d'envoi : {e}")