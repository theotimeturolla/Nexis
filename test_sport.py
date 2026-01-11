import feedparser
import requests

# URLs des flux RSS sport
feeds = {
    "lequipe": "https://www.lequipe.fr/rss/actu_rss.xml",
    "rmc_sport": "https://rmcsport.bfmtv.com/rss/fil-info/",
}

for name, url in feeds.items():
    print(f"\n{'='*50}")
    print(f"🧪 TEST : {name}")
    print(f"URL : {url}")
    print('='*50)
    
    # Test avec requests
    try:
        headers = {"User-Agent": "BotActu/1.0"}
        r = requests.get(url, headers=headers, timeout=5)
        print(f"✅ HTTP Status: {r.status_code}")
    except Exception as e:
        print(f"❌ Erreur requests: {e}")
    
    # Test avec feedparser
    feed = feedparser.parse(url)
    print(f"📊 Bozo (erreur format): {feed.bozo}")
    print(f"📰 Nombre d'entrées: {len(feed.entries)}")
    
    if feed.entries:
        print(f"\n📄 Premier article:")
        print(f"   Titre: {feed.entries[0].title}")
        print(f"   Lien: {feed.entries[0].link}")
    else:
        print("❌ Aucun article trouvé")
        if feed.bozo:
            print(f"⚠️  Erreur: {feed.bozo_exception}")
