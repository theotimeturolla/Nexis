"""
Module d'analyse de sentiment pour les articles.
Utilise TextBlob pour déterminer le sentiment d'un texte.
"""

from textblob import TextBlob
from typing import List, Union
from backend.src.services.scraper.py import ArticleData  # adapte le chemin si besoin
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Classe pour analyser le sentiment des articles."""

    def analyze_text(self, text: str) -> dict:
        """
        Analyse le sentiment d'un texte.
        Retourne un dictionnaire avec polarity et subjectivity.
        Polarity: [-1,1] négatif -> positif
        Subjectivity: [0,1] objectif -> subjectif
        """
        try:
            blob = TextBlob(text)
            return {
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity
            }
        except Exception as e:
            logger.error(f"Erreur analyse sentiment: {e}")
            return {"polarity": 0.0, "subjectivity": 0.0}

    def analyze_articles(
        self, articles: List[Union[ArticleData, dict]]
    ) -> List[Union[ArticleData, dict]]:
        """
        Analyse le sentiment pour chaque article et ajoute le résultat dans une clé 'sentiment'.
        """
        for article in articles:
            text = article.text if isinstance(article, ArticleData) else article.get("text", "")
            sentiment = self.analyze_text(text)
            if isinstance(article, ArticleData):
                article.sentiment = sentiment  # on peut ajouter un attribut dynamique
            else:
                article["sentiment"] = sentiment
        return articles


# =======================
# Exemple d'utilisation
# =======================
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    # Exemple simple
    sample_articles = [
        ArticleData(
            title="Exemple positif",
            url="http://exemple.com",
            source="test",
            topic="économie",
            text="Le marché est en plein essor et les investisseurs sont ravis."
        ),
        ArticleData(
            title="Exemple négatif",
            url="http://exemple.com",
            source="test",
            topic="économie",
            text="La crise économique provoque beaucoup d'inquiétude chez les citoyens."
        )
    ]

    analyzer = SentimentAnalyzer()
    analyzed = analyzer.analyze_articles(sample_articles)

    for a in analyzed:
        print(f"{a.title}: {a.sentiment}")
