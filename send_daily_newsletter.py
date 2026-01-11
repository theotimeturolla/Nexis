#!/usr/bin/env python3
"""
Script pour envoyer la newsletter quotidienne à tous les abonnés
À lancer tous les matins via GitHub Actions
"""

import sys
import os

# Ajout du chemin backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from src.services.subscription_service import SubscriptionService
from src.services.email_service import EmailService
from src.services.scraper import RSSScraper
from src.database import SessionLocal
from src.models import Article

print("=" * 60)
print("🤖 NEXUS - Envoi quotidien de la newsletter")
print("=" * 60)
print()

# ═══════════════════════════════════════════════════════════════
# 1. RÉCUPÉRER LES ABONNÉS
# ═══════════════════════════════════════════════════════════════
print("📧 Récupération des abonnés...")
sub_service = SubscriptionService()
subscribers = sub_service.get_active_subscribers()

if not subscribers:
    print("❌ Aucun abonné actif")
    print("✅ Script terminé")
    sys.exit(0)

print(f"✅ {len(subscribers)} abonné(s) actif(s) :")
for sub in subscribers:
    print(f"   📧 {sub.email}")
print()

# ═══════════════════════════════════════════════════════════════
# 2. SCRAPER LES DERNIERS ARTICLES
# ═══════════════════════════════════════════════════════════════
print("🔍 Scraping des derniers articles...")
scraper = RSSScraper(max_articles_per_topic=10)

topics = ["économie", "politique", "sport", "climat"]
all_articles = []

for topic in topics:
    try:
        print(f"   📰 {topic}...", end=" ")
        articles = scraper.scrape_topic(topic)
        all_articles.extend(articles)
        print(f"✅ {len(articles)} trouvé(s)")
    except Exception as e:
        print(f"❌ Erreur: {e}")

print(f"📊 Total brut : {len(all_articles)} articles")
print()

# ═══════════════════════════════════════════════════════════════
# 3. FALLBACK : SI PEU D'ARTICLES, PRENDRE DEPUIS LA DB
# ═══════════════════════════════════════════════════════════════
if len(all_articles) < 5:
    print("⚠️ Peu d'articles scrapés, récupération depuis la DB...")
    db = SessionLocal()
    all_articles = db.query(Article).order_by(Article.created_at.desc()).limit(10).all()
    db.close()
    print(f"✅ {len(all_articles)} articles récupérés depuis la DB")
    print()

# ═══════════════════════════════════════════════════════════════
# 4. ENVOYER À TOUS LES ABONNÉS
# ═══════════════════════════════════════════════════════════════
print("📧 Envoi de la newsletter...")
email_service = EmailService()
destinataires = [sub.email for sub in subscribers]

try:
    email_service.send_daily_newsletter(
        destinataires=destinataires,
        specific_articles=all_articles
    )
    
    print()
    print("=" * 60)
    print("✅ NEWSLETTER ENVOYÉE AVEC SUCCÈS !")
    print("=" * 60)
    print()
    print(f"📧 {len(destinataires)} destinataire(s) :")
    for email in destinataires:
        print(f"   ✉️  {email}")
    print()
    print(f"📰 {len(all_articles)} article(s) inclus")
    print()
    
except Exception as e:
    print()
    print("=" * 60)
    print("❌ ERREUR LORS DE L'ENVOI")
    print("=" * 60)
    print(f"Erreur : {e}")
    sys.exit(1)
