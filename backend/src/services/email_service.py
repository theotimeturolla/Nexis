import sys
import os

# --- CORRECTIF : BOUSSOLE DES CHEMINS ---
# Permet à Python de trouver le dossier 'src' même si on lance le script depuis ailleurs
current_dir = os.path.dirname(os.path.abspath(__file__)) # Dossier services
backend_dir = os.path.dirname(os.path.dirname(current_dir)) # Dossier backend
if backend_dir not in sys.path:
    sys.path.append(backend_dir)
# ----------------------------------------

import resend
from datetime import datetime
from typing import List
from src.models import Article
from src.database import SessionLocal
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv(os.path.join(backend_dir, ".env"))

# On configure la clé API
resend.api_key = os.getenv("RESEND_API_KEY")

class EmailService:
    def __init__(self):
        self.db = SessionLocal()

    def generate_html(self, articles: List[Article]):
        """Crée le design HTML de la newsletter."""
        if not articles:
            return None

        # Début du HTML (Style simple et propre)
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <div style="background-color: #2c3e50; padding: 20px; text-align: center; color: white;">
                <h1 style="margin:0;">🤖 Nexus Daily</h1>
                <p style="margin:5px 0 0 0; font-size: 14px; opacity: 0.8;">Votre veille intelligente</p>
            </div>
            <div style="padding: 20px;">
        """

        # Boucle sur les articles
        for article in articles:
            # Couleur pastille selon le sentiment
            mood_color = "#95a5a6" # Gris (Neutre)
            if article.sentiment_label == "positif": mood_color = "#27ae60" # Vert
            if article.sentiment_label == "négatif": mood_color = "#c0392b" # Rouge

            # Carte Article
            html_content += f"""
            <div style="border: 1px solid #eee; border-radius: 8px; margin-bottom: 20px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <div style="display:flex; align-items:center; margin-bottom:10px;">
                    <span style="background-color:{mood_color}; color:white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight:bold;">
                        {article.sentiment_label.upper() if article.sentiment_label else "NEUTRE"}
                    </span>
                    <span style="margin-left: 10px; font-size: 12px; color: #7f8c8d;">
                        {article.topic.upper() if article.topic else "ACTU"} • Source: {article.source or "Web"}
                    </span>
                </div>
                
                <h2 style="margin: 0 0 10px 0; font-size: 18px;">
                    <a href="{article.url}" style="text-decoration: none; color: #2c3e50;">{article.title}</a>
                </h2>
                
                <p style="font-size: 14px; line-height: 1.5; color: #555; background-color: #f9f9f9; padding: 10px; border-left: 3px solid #3498db;">
                    <strong>🤖 Résumé IA :</strong> {article.summary or "Pas de résumé disponible."}
                </p>
                
                <div style="font-size: 12px; color: #999; margin-top: 10px; border-top: 1px solid #eee; padding-top: 5px;">
                     🛡️ Fiabilité : <strong>{article.reliability_score}/100</strong> ({article.source_count} sources citées)
                </div>
            </div>
            """

        # Fin du HTML
        html_content += """
            </div>
            <div style="text-align: center; padding: 20px; font-size: 12px; color: #aaa;">
                Généré par Nexus AI • <a href="#">Se désabonner</a>
            </div>
        </body>
        </html>
        """
        return html_content

    def send_newsletter(self, recipient_email: str):
        """Récupère les nouveautés et envoie l'email."""
        # On prend les 5 derniers articles ajoutés
        articles = self.db.query(Article).order_by(Article.created_at.desc()).limit(5).all()
        
        if not articles:
            print("📭 Pas d'articles à envoyer.")
            return

        print(f"📧 Préparation de la newsletter avec {len(articles)} articles...")
        email_html = self.generate_html(articles)

        try:
            if not resend.api_key:
                print("❌ ERREUR: Clé API Resend manquante dans le fichier .env")
                return

            r = resend.Emails.send({
                "from": "Nexus Bot <onboarding@resend.dev>",
                "to": recipient_email,
                "subject": f"📢 Nexus : L'actu du {datetime.now().strftime('%d/%m')}",
                "html": email_html
            })
            print(f"✅ Email envoyé avec succès ! ID: {r.get('id')}")
        except Exception as e:
            print(f"❌ Erreur envoi email : {e}")

# Test rapide
if __name__ == "__main__":
    service = EmailService()
    # 👇 REMPLACEZ CECI PAR VOTRE VRAI EMAIL 👇
    service.send_newsletter("juleschopard11@gmail.com")