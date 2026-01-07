import logging
import spacy
from typing import List, Optional
from pydantic import BaseModel
from transformers import pipeline

logger = logging.getLogger(__name__)

# --- MODÈLES DE DONNÉES ---
class SourceEntity(BaseModel):
    name: str
    type: str  # 'Personne' ou 'Organisation'
    count: int

class ArticleAnalysis(BaseModel):
    summary: str
    sources: List[SourceEntity]
    reliability_score: int

class LLMProcessor:
    def __init__(self):
        print("⏳ Chargement des modèles IA (ça peut être long au 1er lancement)...")
        
        # 1. Résumeur (Modèle Facebook BART)
        try:
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        except Exception as e:
            logger.error(f"Erreur summarizer: {e}")
            self.summarizer = None

        # 2. Analyseur de Sources (SpaCy)
        try:
            self.nlp = spacy.load("fr_core_news_md")
        except Exception as e:
            logger.error(f"Erreur SpaCy: {e}")
            self.nlp = None

    def analyze_content(self, text: str) -> Optional[ArticleAnalysis]:
        if not text or len(text) < 200:
            return None

        # A. GÉNÉRATION DU RÉSUMÉ
        summary_text = "Non disponible"
        if self.summarizer:
            try:
                # On coupe le texte pour ne pas saturer la mémoire
                truncated = text[:3000]
                res = self.summarizer(truncated, max_length=130, min_length=30, do_sample=False)
                summary_text = res[0]['summary_text']
            except Exception as e:
                logger.error(f"Erreur résumé : {e}")

        # B. EXTRACTION DES SOURCES (Source Pyramid)
        found_sources = []
        score = 50 

        if self.nlp:
            doc = self.nlp(text)
            entities = {}
            # On cherche les noms de personnes (PER) et organisations (ORG)
            for ent in doc.ents:
                if ent.label_ in ["PER", "ORG"]: 
                    name = ent.text.strip().replace("\n", " ")
                    if name not in entities:
                        entities[name] = {"type": ent.label_, "count": 0}
                    entities[name]["count"] += 1
            
            for name, data in entities.items():
                sType = "Personne" if data["type"] == "PER" else "Organisation"
                found_sources.append(SourceEntity(name=name, type=sType, count=data["count"]))

            # C. SCORE DE FIABILITÉ (Logique simple)
            # + de sources citées = article potentiellement plus sourcé
            score = min(100, 40 + (len(found_sources) * 5))

        return ArticleAnalysis(
            summary=summary_text,
            sources=found_sources,
            reliability_score=score
        )