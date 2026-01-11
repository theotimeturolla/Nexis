import feedparser
import requests

# Nouvelles URLs à tester
feeds = {
    "lequipe_general": "https://www.lequipe.fr/rss/actu_rss.xml",
    "lequipe_all": "https://www.lequipe.fr/rss",
    "google_sport": "https://news.google.com/rss/search?q=sport&hl=fr&gl=FR&ceid=FR:fr",
    "google_tennis": "https://news.google.com/rss/search?q=tennis&hl=fr&gl=FR&ceid=FR:fr",
    "eurosport": "https://www.eurosport.fr/rss.xml",
    "sports_fr": "https://www.sport.fr/rss/sport.rss",
    "20minutes_sport": "https://www.20minutes.fr/feeds/rss-sport.xml",
}

print("🔍 TEST DES FLUX RSS SPORT\n")

for name, url in feeds.items():
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=5)
        feed = feedparser.parse(url)
        
        if r.status_code == 200 and len(feed.entries) > 0:
            print(f"✅ {name:20} | {len(feed.entries):2} articles | {url}")
        else:
            print(f"❌ {name:20} | Status: {r.status_code} | 0 articles")
    except Exception as e:
        print(f"❌ {name:20} | Erreur: {str(e)[:50]}")

print("\n" + "="*80)
