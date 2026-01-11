from backend.src.services.news_api_service import NewsAPIService

print("🧪 TEST NEWSAPI\n")

# Initialisation
service = NewsAPIService()

# Test 1 : Recherche tennis
print("\n--- TEST 1 : Recherche 'tennis' ---")
articles = service.search_articles("tennis", max_results=3)

for i, art in enumerate(articles, 1):
    print(f"\n{i}. {art['title']}")
    print(f"   Source: {art['source']}")
    print(f"   URL: {art['url'][:50]}...")

# Test 2 : Headlines sport
print("\n--- TEST 2 : Top headlines sport ---")
headlines = service.get_top_headlines(category='sports', max_results=3)

for i, art in enumerate(headlines, 1):
    print(f"\n{i}. {art['title']}")
    print(f"   Source: {art['source']}")
