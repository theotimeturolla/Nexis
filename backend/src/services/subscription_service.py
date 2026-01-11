import os
import resend
from datetime import datetime
from dotenv import load_dotenv
from src.database import SessionLocal
from src.models import Subscriber

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

class SubscriptionService:
    """Gestion des abonnements à la newsletter"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def subscribe(self, email: str) -> dict:
        """Abonner un email et envoyer confirmation"""
        
        # Vérifier si déjà abonné
        existing = self.db.query(Subscriber).filter(Subscriber.email == email).first()
        
        if existing:
            if existing.is_active:
                return {
                    "success": False,
                    "message": f"✅ {email} est déjà abonné !"
                }
            else:
                # Réactiver l'abonnement
                existing.is_active = 1
                self.db.commit()
                self.send_confirmation_email(email)
                return {
                    "success": True,
                    "message": f"✅ Abonnement réactivé pour {email} !"
                }
        
        # Créer nouvel abonné
        new_subscriber = Subscriber(email=email)
        self.db.add(new_subscriber)
        self.db.commit()
        
        # Envoyer email de confirmation
        self.send_confirmation_email(email)
        
        return {
            "success": True,
            "message": f"✅ Abonnement confirmé pour {email} !\n\n📧 Un email de bienvenue a été envoyé."
        }
    
    def unsubscribe(self, email: str) -> dict:
        """Désabonner un email"""
        subscriber = self.db.query(Subscriber).filter(Subscriber.email == email).first()
        
        if not subscriber:
            return {"success": False, "message": "Email non trouvé"}
        
        subscriber.is_active = 0
        self.db.commit()
        
        return {"success": True, "message": f"Désabonnement effectué pour {email}"}
    
    def get_active_subscribers(self):
        """Récupérer tous les abonnés actifs"""
        return self.db.query(Subscriber).filter(Subscriber.is_active == 1).all()
    
    def send_confirmation_email(self, email: str):
        """Envoyer l'email de confirmation d'abonnement"""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; text-align: center; border-radius: 10px;">
                <h1 style="color: white; margin: 0; font-size: 32px;">🤖 Bienvenue chez Nexus !</h1>
            </div>
            
            <div style="padding: 30px; background: #f9f9f9; border-radius: 10px; margin-top: 20px;">
                <h2 style="color: #333;">Abonnement confirmé ! 🎉</h2>
                
                <p style="font-size: 16px; color: #555; line-height: 1.6;">
                    Merci de vous être abonné à la newsletter <strong>Nexus</strong>.
                </p>
                
                <p style="font-size: 16px; color: #555; line-height: 1.6;">
                    Vous recevrez désormais <strong>tous les matins</strong> une sélection des articles 
                    les plus importants, analysés et résumés par notre intelligence artificielle.
                </p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #667eea; margin-top: 0;">📊 Ce que vous recevrez :</h3>
                    <ul style="color: #555; line-height: 1.8;">
                        <li>✅ Articles sélectionnés par Gemini AI</li>
                        <li>😊 Analyse de sentiment (positif/négatif/neutre)</li>
                        <li>📝 Résumés automatiques par IA</li>
                        <li>🌐 Sources vérifiées et fiables</li>
                    </ul>
                </div>
                
                <p style="font-size: 14px; color: #888; text-align: center; margin-top: 30px;">
                    Email envoyé à : <strong>{email}</strong>
                </p>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #888; font-size: 12px;">
                <p>Nexus AI - Votre veille intelligente</p>
            </div>
        </body>
        </html>
        """
        
        try:
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": email,
                "subject": "🎉 Bienvenue chez Nexus - Abonnement confirmé !",
                "html": html_content
            })
            print(f"✅ Email de confirmation envoyé à {email}")
        except Exception as e:
            print(f"❌ Erreur envoi email de confirmation : {e}")
