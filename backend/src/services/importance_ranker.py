import os
import google.generativeai as genai
from typing import List
from dotenv import load_dotenv
from src.models import Article

load_dotenv()

class ImportanceRanker:
    """Classe les articles par importance avec Gemini AI"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ GEMINI_API_KEY manquante dans .env")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("✅ Gemini AI initialisé")
    
    def rank_articles(self, articles: List[Article], top_n: int = 10) -> List[Article]:
        """
        Classe les articles par importance journalistique
        
        Args:
            articles: Liste d'articles à classer
            top_n: Nombre d'articles à retourner
            
        Returns:
            Liste des top_n articles les plus importants
        """
        
        if not self.model:
            print("❌ Gemini non disponible, tri par date")
            return articles[:top_n]
        
        if len(articles) <= top_n:
            return articles
        
        try:
            # Préparer les titres pour Gemini
            titles_text = "\n".join([
                f"{i+1}. [{art.source}] {art.title}"
                for i, art in enumerate(articles)
            ])
            
            prompt = f"""Tu es un rédacteur en chef expérimenté d'un journal français.

Classe ces {len(articles)} articles par ordre d'IMPORTANCE JOURNALISTIQUE (du plus important au moins important).

**Critères de priorité :**
1. Impact majeur sur la société (politique, économie, santé publique)
2. Urgence de l'information (événements en cours)
3. Portée large (national > local, international > national si majeur)
4. Fiabilité de la source (grands médias > petits sites)
5. Nouveauté réelle (pas des redites)

**Articles :**
{titles_text}

**IMPORTANT :** Réponds UNIQUEMENT avec les numéros des {top_n} articles les plus importants, séparés par des virgules, SANS AUCUN AUTRE TEXTE.

Exemple de réponse : 3,7,1,12,5,18,2,9,14,6"""

            print(f"🤖 Gemini analyse {len(articles)} articles...")
            response = self.model.generate_content(prompt)
            
            # Parser la réponse
            response_text = response.text.strip()
            rankings = [int(n.strip()) - 1 for n in response_text.split(",")]
            
            # Retourner les articles dans l'ordre d'importance
            selected = [articles[i] for i in rankings if 0 <= i < len(articles)]
            
            print(f"✅ Top {len(selected[:top_n])} articles sélectionnés par Gemini")
            return selected[:top_n]
        
        except Exception as e:
            print(f"❌ Erreur Gemini : {e}")
            print("⚠️ Fallback : tri par date")
            return articles[:top_n]


# Test rapide
if __name__ == "__main__":
    ranker = ImportanceRanker()
    print("✅ Ranker initialisé avec succès")
