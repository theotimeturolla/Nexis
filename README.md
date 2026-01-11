# 🤖 Nexus - Newsletter Intelligente avec IA

> Système de veille automatisé propulsé par l'intelligence artificielle pour une curation d'actualités personnalisée

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions)](https://github.com/features/actions)
[![Gradio](https://img.shields.io/badge/Interface-Gradio-orange.svg)](https://gradio.app/)

## 📋 Table des matières

- [À propos](#à-propos)
- [Fonctionnalités](#fonctionnalités)
- [Technologies](#technologies)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Automatisation](#automatisation)
- [API et Services](#api-et-services)
- [Contribution](#contribution)
- [Roadmap](#roadmap)
- [Licence](#licence)

## 📖 À propos

**Nexus** est une plateforme de veille automatisée qui combine plusieurs technologies d'intelligence artificielle pour offrir une expérience de curation d'actualités de nouvelle génération. Le système collecte, analyse, résume et distribue automatiquement les articles les plus pertinents à vos abonnés.

### Pourquoi Nexus ?

- **Intelligence artificielle avancée** : Utilisation de Gemini AI pour sélectionner les articles les plus importants
- **Analyse de sentiment** : Classification automatique des articles (positif/neutre/négatif) via BERT
- **Résumés automatiques** : Génération de résumés concis par transformers
- **Automatisation complète** : Envoi quotidien automatique via GitHub Actions
- **Interface moderne** : Application web intuitive avec Gradio
- **Système d'abonnement** : Gestion complète des abonnés avec emails de confirmation

## ✨ Fonctionnalités

### 🔍 Collecte et Analyse

- **Multi-sources** : Agrégation d'articles depuis NewsAPI et flux RSS français
- **Scraping intelligent** : Extraction automatique du contenu complet des articles
- **Filtrage par mots-clés** : Recherche ciblée d'articles sur des sujets précis
- **Déduplication** : Évite les doublons grâce à l'indexation des URLs

### 🧠 Intelligence Artificielle

- **Sélection par IA** : Gemini AI classe les articles par importance journalistique
- **Analyse de sentiment** : Modèle BERT multilingue pour détecter le ton des articles
- **Résumés automatiques** : Génération de synthèses via Facebook BART
- **Extraction d'entités** : Identification des sources citées avec SpaCy
- **Score de fiabilité** : Évaluation automatique de la crédibilité des articles

### 📧 Distribution

- **Système d'abonnement** : Gestion complète de la base d'abonnés
- **Emails de bienvenue** : Confirmation automatique avec design HTML
- **Newsletters quotidiennes** : Envoi automatisé tous les matins à 7h UTC
- **Design responsive** : Emails adaptés à tous les appareils
- **Désabonnement** : Gestion des désabonnements en un clic

### 🖥️ Interface Web

- **Recherche d'articles** : Moteur de recherche intégré avec affichage des résultats
- **Tableau de bord** : Visualisation des derniers articles collectés
- **Abonnement en ligne** : Formulaire d'inscription accessible
- **Statistiques** : Graphiques interactifs (sentiments, sources)
- **Envoi manuel** : Possibilité d'envoyer des newsletters à la demande

## 🛠️ Technologies

### Backend

| Technologie | Rôle | Version |
|------------|------|---------|
| **Python** | Langage principal | 3.11+ |
| **FastAPI** | Framework web | 0.104.1 |
| **SQLAlchemy** | ORM base de données | 2.0.23 |
| **SQLite** | Base de données | - |

### Intelligence Artificielle

| Modèle | Utilisation | Provider |
|--------|-------------|----------|
| **Gemini 2.0 Flash** | Sélection d'articles | Google AI |
| **BERT Multilingual** | Analyse de sentiment | Hugging Face |
| **Facebook BART** | Résumés automatiques | Hugging Face |
| **SpaCy fr_core_news_md** | NER (entités nommées) | SpaCy |

### Services Externes

| Service | Fonction | Quota |
|---------|----------|-------|
| **NewsAPI** | Source d'articles | 100 req/jour |
| **Resend** | Envoi d'emails | 100 emails/jour |
| **Gemini API** | Traitement IA | 60 req/min |

### Frontend & Interface

- **Gradio** : Interface web interactive
- **Plotly** : Visualisations de données
- **Pandas** : Manipulation de données

### DevOps & Automatisation

- **GitHub Actions** : CI/CD et automatisation
- **Git** : Versioning
- **pip** : Gestion des dépendances

## 🏗️ Architecture

### Flux de Données

```
┌─────────────┐
│  NewsAPI    │──┐
└─────────────┘  │
                 │
┌─────────────┐  │    ┌──────────────┐
│  Flux RSS   │──┼───▶│   Scraper    │
└─────────────┘  │    └──────┬───────┘
                 │           │
┌─────────────┐  │           ▼
│  Recherche  │──┘    ┌──────────────┐
└─────────────┘       │  Articles    │
                      │  bruts       │
                      └──────┬───────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐    ┌──────────────┐    ┌──────────────┐
│ Gemini AI     │    │  BERT        │    │  BART        │
│ (Importance)  │    │  (Sentiment) │    │  (Résumé)    │
└───────┬───────┘    └──────┬───────┘    └──────┬───────┘
        │                   │                    │
        └───────────────────┼────────────────────┘
                            ▼
                    ┌──────────────┐
                    │  SQLite DB   │
                    │  (Articles)  │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐  ┌──────────────┐
│  Interface   │   │  Newsletter  │  │  GitHub      │
│  Gradio      │   │  manuelle    │  │  Actions     │
└──────────────┘   └──────────────┘  └──────┬───────┘
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │  Abonnés     │
                                    │  (Resend)    │
                                    └──────────────┘
```

### Architecture Modulaire

```
Nexus/
├── backend/
│   ├── src/
│   │   ├── services/
│   │   │   ├── scraper.py              # Collecte d'articles
│   │   │   ├── sentiment_analyzer.py   # Analyse BERT
│   │   │   ├── importance_ranker.py    # Classement Gemini
│   │   │   ├── llm_processor.py        # Résumés & NER
│   │   │   ├── news_api_service.py     # Client NewsAPI
│   │   │   ├── email_service.py        # Génération emails
│   │   │   └── subscription_service.py # Gestion abonnés
│   │   ├── models.py                   # Modèles de données
│   │   └── database.py                 # Connexion DB
│   └── init_db.py                      # Initialisation DB
├── interface.py                        # Application Gradio
├── send_daily_newsletter.py            # Script quotidien
├── main.py                             # CLI legacy
└── .github/workflows/daily.yml         # Automatisation
```

## 🚀 Installation

### Prérequis

- Python 3.11 ou supérieur
- Git
- pip (gestionnaire de paquets Python)
- 2 Go de RAM minimum (pour les modèles IA)

### Installation locale

#### 1. Cloner le repository

```bash
git clone https://github.com/theotimeturolla/Nexis.git
cd Nexis
```

#### 2. Créer un environnement virtuel

```bash
python -m venv .venv

# Activation (Linux/Mac)
source .venv/bin/activate

# Activation (Windows)
.venv\Scripts\activate
```

#### 3. Installer les dépendances

```bash
pip install -r backend/requirements.txt
```

#### 4. Télécharger les modèles SpaCy

```bash
python -m spacy download fr_core_news_md
```

#### 5. Initialiser la base de données

```bash
python backend/init_db.py
```

### Lancement rapide

#### Windows
Double-cliquez sur `Lancer_Nexus.bat`

#### Linux/Mac
```bash
bash lancer_nexus.sh
```

#### Manuel
```bash
python interface.py
```

L'interface s'ouvre automatiquement sur `http://localhost:7860`

## ⚙️ Configuration

### Variables d'environnement

Créez un fichier `backend/.env` :

```env
# API NewsAPI (https://newsapi.org)
NEWSAPI_KEY=votre_cle_newsapi

# API Resend (https://resend.com)
RESEND_API_KEY=votre_cle_resend

# API Gemini (https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=votre_cle_gemini
```

### Obtenir les clés API

#### NewsAPI (Gratuit - 100 requêtes/jour)
1. Créer un compte sur [newsapi.org](https://newsapi.org)
2. Récupérer la clé dans le dashboard
3. Ajouter dans `.env`

#### Resend (Gratuit - 100 emails/jour)
1. Créer un compte sur [resend.com](https://resend.com)
2. Générer une API key
3. Ajouter dans `.env`

#### Gemini AI (Gratuit - 60 req/min)
1. Aller sur [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Créer une API key
3. Ajouter dans `.env`

### Configuration GitHub Actions (Optionnel)

Pour l'envoi automatique quotidien :

1. Aller dans Settings → Secrets → Actions
2. Ajouter les 3 secrets :
   - `NEWSAPI_KEY`
   - `RESEND_API_KEY`
   - `GEMINI_API_KEY`

## 📖 Utilisation

### Interface Graphique

#### Recherche d'articles

1. Ouvrir l'onglet **🔍 Recherche**
2. Entrer un mot-clé (ex: "football", "économie")
3. Cliquer sur **Chercher**
4. Les articles s'affichent avec sentiment et source

#### Abonnement à la newsletter

1. Ouvrir l'onglet **✉️ S'abonner**
2. Entrer une adresse email
3. Cliquer sur **S'abonner**
4. Un email de confirmation est envoyé immédiatement
5. Les newsletters seront envoyées tous les matins à 7h

#### Envoi manuel

1. Rechercher des articles (ou utiliser les articles existants)
2. Aller dans l'onglet **📧 Envoyer Email**
3. Cliquer sur **Envoyer la Newsletter à tous les abonnés**
4. Tous les abonnés actifs reçoivent l'email

#### Statistiques

1. Ouvrir l'onglet **📊 Statistiques**
2. Cliquer sur **Générer les Statistiques**
3. Voir :
   - Répartition des sentiments (graphique circulaire)
   - Top 10 sources (graphique en barres)
   - Statistiques textuelles

### Ligne de commande (Legacy)

```bash
# Lancer le CLI interactif
python main.py
```

Commandes disponibles :
- `cherche [mot-clé]` : Rechercher des articles
- `liste` : Afficher les derniers articles
- `stats` : Voir les statistiques
- `envoie mail` : Envoyer la newsletter
- `stop` : Quitter

### Script automatisé

```bash
# Envoi immédiat à tous les abonnés
python send_daily_newsletter.py
```

Ce script :
1. Scrape les articles sur économie, politique, sport, climat
2. Analyse et classe les articles avec Gemini AI
3. Envoie la newsletter à tous les abonnés actifs
4. Sauvegarde la base de données

## 📁 Structure du projet

```
Nexus/
│
├── 📄 README.md                          # Documentation principale
├── 📄 .gitignore                         # Fichiers ignorés par Git
├── 📄 requirements.txt                   # Dépendances Python
│
├── 🖥️ interface.py                       # Application Gradio (interface web)
├── 📧 send_daily_newsletter.py           # Script d'envoi quotidien
├── 💻 main.py                            # CLI interactif (legacy)
│
├── 🦇 Lancer_Nexus.bat                   # Lanceur Windows
├── 🐧 lancer_nexus.sh                    # Lanceur Linux/Mac
│
├── 🗄️ nexis.db                           # Base de données SQLite
│
├── 🧪 test_*.py                          # Scripts de test
│
├── 📂 backend/                           # Code backend
│   ├── 📂 src/
│   │   ├── 📄 database.py                # Configuration SQLAlchemy
│   │   ├── 📄 models.py                  # Modèles Article & Subscriber
│   │   │
│   │   └── 📂 services/                  # Services métier
│   │       ├── 📄 scraper.py             # Collecte NewsAPI + RSS
│   │       ├── 📄 news_api_service.py    # Client NewsAPI
│   │       ├── 📄 sentiment_analyzer.py  # Analyse BERT
│   │       ├── 📄 importance_ranker.py   # Classement Gemini
│   │       ├── 📄 llm_processor.py       # Résumés & NER
│   │       ├── 📄 email_service.py       # Génération emails HTML
│   │       └── 📄 subscription_service.py # Gestion abonnés
│   │
│   ├── 📄 init_db.py                     # Initialisation base de données
│   ├── 📄 requirements.txt               # Dépendances
│   └── 📄 .env                           # Variables d'environnement (à créer)
│
└── 📂 .github/
    └── 📂 workflows/
        └── 📄 daily.yml                  # GitHub Actions (automatisation)
```

## ⏰ Automatisation

### GitHub Actions

Le fichier `.github/workflows/daily.yml` configure l'envoi automatique quotidien.

#### Déclencheurs

- **Cron** : Tous les jours à 7h00 UTC (8h France hiver, 9h France été)
- **Manuel** : Via le bouton "Run workflow" sur GitHub

#### Workflow

```yaml
1. Récupération du code
2. Installation Python 3.11
3. Installation des dépendances
4. Restauration de la base de données
5. 🤖 Envoi de la newsletter quotidienne
   - Scraping des derniers articles
   - Sélection avec Gemini AI
   - Envoi à tous les abonnés
6. Sauvegarde de la base de données
```

#### Configuration requise

1. Forker le repository ou l'avoir en propre
2. Ajouter les secrets dans Settings → Secrets → Actions
3. Activer GitHub Actions
4. Le workflow se lancera automatiquement chaque matin

#### Test manuel

1. Aller dans l'onglet **Actions** sur GitHub
2. Sélectionner **Nexus Daily Newsletter**
3. Cliquer sur **Run workflow**
4. Choisir la branche **main**
5. Cliquer sur **Run workflow** (bouton vert)
6. Suivre l'exécution en temps réel dans les logs

## 🔌 API et Services

### NewsAPI

**Endpoint** : `https://newsapi.org/v2/everything`

**Quota** : 100 requêtes/jour (gratuit)

**Utilisation** :
- Recherche d'articles français récents
- Filtrage par mot-clé
- Classement par pertinence

### Gemini AI

**Modèle** : `gemini-2.0-flash-exp`

**Quota** : 60 requêtes/minute (gratuit)

**Utilisation** :
- Classement des articles par importance journalistique
- Sélection des 10 meilleurs articles parmi 20+
- Critères : impact, urgence, portée, fiabilité

### BERT Sentiment Analysis

**Modèle** : `nlptown/bert-base-multilingual-uncased-sentiment`

**Utilisation** :
- Classification 1-5 étoiles
- Conversion en positif/neutre/négatif
- Score de confiance

### Resend

**Endpoint** : `https://api.resend.com/emails`

**Quota** : 100 emails/jour (gratuit)

**Utilisation** :
- Envoi des newsletters HTML
- Emails de confirmation d'abonnement
- Gestion de la délivrabilité

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment participer :

### 1. Fork le projet

```bash
# Cliquer sur "Fork" en haut à droite sur GitHub
```

### 2. Créer une branche

```bash
git checkout -b feature/amelioration-incroyable
```

### 3. Commiter les changements

```bash
git add .
git commit -m "Ajout d'une fonctionnalité géniale"
```

### 4. Pousser vers la branche

```bash
git push origin feature/amelioration-incroyable
```

### 5. Ouvrir une Pull Request

Sur GitHub, cliquer sur "New Pull Request"

### Guidelines

- Suivre le style de code existant
- Ajouter des tests si nécessaire
- Mettre à jour la documentation
- Décrire clairement les changements

## 🗺️ Roadmap

### Version 2.0 (En cours)

- [ ] Support multi-langues (EN, ES, DE)
- [ ] Filtres personnalisés par utilisateur
- [ ] API REST complète
- [ ] Application mobile (React Native)
- [ ] Intégration Slack/Discord

### Version 3.0 (Futur)

- [ ] Recommandations personnalisées (ML)
- [ ] Chatbot IA pour recherche conversationnelle
- [ ] Podcast audio généré automatiquement
- [ ] Détection de fake news
- [ ] Thèmes personnalisables

### Améliorations continues

- [x] Interface graphique Gradio
- [x] Système d'abonnement complet
- [x] Sélection intelligente Gemini AI
- [x] Automatisation GitHub Actions
- [ ] Cache Redis pour performance
- [ ] Monitoring avec Grafana
- [ ] Tests unitaires (>80% coverage)

## 📄 Licence

Ce projet est sous licence **MIT**.

```
MIT License

Copyright (c) 2026 Théotime Turolla

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👤 Auteur

**Théotime Turolla**

- GitHub: [@theotimeturolla](https://github.com/theotimeturolla)
- Repository: [Nexis](https://github.com/theotimeturolla/Nexis)

## 🙏 Remerciements

- **NewsAPI** pour l'accès aux articles d'actualité
- **Google** pour Gemini AI
- **Hugging Face** pour les modèles BERT et BART
- **SpaCy** pour le traitement du langage naturel
- **Gradio** pour l'interface utilisateur
- **Resend** pour l'envoi d'emails
- La communauté **Open Source** pour les outils et bibliothèques

## 📊 Statistiques du projet

![GitHub stars](https://img.shields.io/github/stars/theotimeturolla/Nexis?style=social)
![GitHub forks](https://img.shields.io/github/forks/theotimeturolla/Nexis?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/theotimeturolla/Nexis?style=social)

---

<p align="center">
  Fait avec ❤️ et 🤖 par <a href="https://github.com/theotimeturolla">Théotime Turolla</a>
</p>

<p align="center">
  <sub>Propulsé par l'intelligence artificielle • Nexus © 2026</sub>
</p>
