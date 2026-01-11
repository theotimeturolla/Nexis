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
        """Crée le design HTML de la newsletter avec analyse de sentiment"""
        if not articles:
            return None
        
        items_html = ""
        for art in articles:
            # 🎨 Couleur selon le sentiment
            sentiment_colors = {
                "positif": "#10b981",   # Vert
                "négatif": "#ef4444",   # Rouge  
                "neutre": "#f59e0b"     # Orange
            }
            color = sentiment_colors.get(art.sentiment_label.lower(), "#6b7280")
            
            # Emoji selon le sentiment
            sentiment_emojis = {
                "positif": "😊",
                "négatif": "😞",
                "neutre": "😐"
            }
            emoji = sentiment_emojis.get(art.sentiment_label.lower(), "📰")
            
            items_html += f"""
            <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid {color}; background: #f9f9f9; border-radius: 5px;">
                <h3 style="margin: 0 0 10px 0; color: #333;">
                    {emoji} {art.title}
                </h3>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">
                    <strong>Source:</strong> {art.source} | 
                    <strong>Sujet:</strong> {art.topic.upper()} | 
                    <span style="color: {color}; font-weight: bold;">
                        Sentiment: {art.sentiment_label.upper()} {emoji}
                    </span>
                </p>
                <p style="color: #555; font-size: 14px; line-height: 1.6; margin: 10px 0;">
                    <strong>📝 Résumé IA:</strong> {art.summary or "Non disponible"}
                </p>
                <p style="margin: 10px 0 0 0;">
                    <a href="{art.url}" style="display: inline-block; padding: 8px 16px; background-color: {color}; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
                        Lire l'article complet →
                    </a>
                </p>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">
            <div style="background-color: #2563eb; padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0;">
                <h1 style="margin:0; font-size: 28px;">🤖 Nexus Daily</h1>
                <p style="margin:10px 0 0 0; font-size: 14px; opacity: 0.9;">
                    Votre revue de presse intelligente avec analyse de sentiment
                </p>
            </div>
            <div style="background-color: white; padding: 20px; border-radius: 0 0 10px 10px;">
                <p style="color: #666; font-size: 14px;">
                    📅 {len(articles)} articles sélectionnés pour vous
                </p>
                {items_html}
            </div>
            <div style="text-align: center; padding: 20px; font-size: 12px; color: #888;">
                <p>Généré par Nexus AI Agent 🤖</p>
                <p style="margin: 5px 0;">
                    😊 Positif | 😐 Neutre | 😞 Négatif
                </p>
            </div>
        </body>
        </html>
        """

    def send_daily_newsletter(self, destinataires: List[str], specific_articles: List[Article] = None):
        """Envoie la newsletter quotidienne avec analyse de sentiment"""
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
                "subject": f"📢 Nexus : {len(articles)} Nouveaux Articles avec Analyse de Sentiment",
                "html": html_content
            })
            print(f"✅ Email envoyé ! ID: {r.get('id')}")
        except Exception as e:
            print(f"❌ Erreur d'envoi : {e}")