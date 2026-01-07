import sys
import os
import logging
from datetime import datetime

# Configuration des logs pour voir ce qui se passe
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ajout du dossier backend au chemin pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "backend"))

from src.services.scraper import RSSScraper
from src.services.email_service import EmailService

def job():
    print("\n" + "="*50)
    print(f"🚀 LANCEMENT DU ROBOT NEXUS - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*50 + "\n")

    # 1. SCRAPING
    print("1️⃣  Phase de lecture des news...")
    scraper = RSSScraper(max_articles_per_topic=4) # 3 articles max par sujet pour commencer
    
    # On définit vos sujets préférés
    topics = ["économie", "climat", "politique", "géopolitique", "sport"]
    
    total_new_articles = 0
    for topic in topics:
        try:
            logging.info(f"Analyse du sujet : {topic}")
            new_articles = scraper.scrape_topic(topic)
            total_new_articles += len(new_articles)
        except Exception as e:
            logging.error(f"Erreur sur {topic}: {e}")

    print(f"\n📊 Bilan : {total_new_articles} nouveaux articles trouvés et mémorisés.\n")

 
# 2. ENVOI EMAIL (Seulement s'il y a du nouveau)
    if total_new_articles > 0:
        print("2️⃣  Phase d'expédition de l'email...")
        emailer = EmailService()
        
        # 👇 LISTE DES DESTINATAIRES 👇
        # Ajoutez autant d'emails que vous voulez, séparés par des virgules
        destinataires = [
            "juleschopard11@gmail.com",
            "MonaGramdi@gmail.com",
            # "un_autre_ami@exemple.com"
        ]
        
        # La boucle magique : on envoie à chacun, un par un
        for personne in destinataires:
            print(f"   ➡️ Envoi en cours vers {personne}...")
            try:
                emailer.send_newsletter(personne)
                print(f"   ✅ Envoyé à {personne} !")
            except Exception as e:
                print(f"   ❌ Échec pour {personne} : {e}")
                
    else:
        print("😴 Pas de nouveautés, pas d'email envoyé. Le robot retourne dormir.")
    print("\n" + "="*50)
    print("👋 FIN DU PROGRAMME")
    print("="*50)

if __name__ == "__main__":
    job()