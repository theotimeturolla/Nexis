import requests
import feedparser

# On teste avec Le Monde (plus permissif que Google)
url = "https://www.lemonde.fr/politique/rss_full.xml"

print(f"--- TEST DE CONNEXION VERS : {url} ---")

# 1. Test via Requests (Simule un navigateur)
headers = {"User-Agent": "Mozilla/5.0"}
try:
    response = requests.get(url, headers=headers, timeout=5)
    print(f"✅ STATUS HTTP : {response.status_code} (200 est bon)")
except Exception as e:
    print(f"❌ ERREUR REQUESTS : {e}")

# 2. Test via Feedparser direct
print("\n--- TEST FEEDPARSER ---")
feed = feedparser.parse(url)
print(f"Bozo (Erreur format) : {feed.bozo}")
if feed.bozo:
    print(f"Détail erreur : {feed.bozo_exception}")
print(f"Nombre d'entrées trouvées : {len(feed.entries)}")