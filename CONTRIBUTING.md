# Guide de Contribution

Merci de votre intérêt pour contribuer à Nexus ! Ce document vous guidera à travers le processus de contribution.

## Code de Conduite

En participant à ce projet, vous acceptez de respecter notre code de conduite. Soyez respectueux, constructif et professionnel dans toutes vos interactions.

## Comment contribuer ?

### Signaler un bug

1. Vérifiez que le bug n'a pas déjà été signalé dans les [Issues](https://github.com/theotimeturolla/Nexis/issues)
2. Ouvrez une nouvelle issue avec le label `bug`
3. Incluez :
   - Description détaillée du problème
   - Étapes pour reproduire le bug
   - Comportement attendu vs comportement observé
   - Version de Python et du système d'exploitation
   - Logs d'erreur si disponibles

### Proposer une fonctionnalité

1. Ouvrez une issue avec le label `enhancement`
2. Décrivez clairement :
   - Le problème que cette fonctionnalité résout
   - La solution proposée
   - Des alternatives envisagées
   - Des captures d'écran/mockups si applicable

### Soumettre une Pull Request

#### 1. Fork et Clone

```bash
# Fork le repository sur GitHub puis :
git clone https://github.com/votre-username/Nexis.git
cd Nexis
```

#### 2. Créer une branche

```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
```

Conventions de nommage :
- `feature/` : Nouvelle fonctionnalité
- `fix/` : Correction de bug
- `docs/` : Documentation
- `refactor/` : Refactoring de code
- `test/` : Ajout de tests

#### 3. Faire vos modifications

- Suivez le style de code existant
- Commentez le code complexe
- Ajoutez des docstrings aux fonctions
- Mettez à jour la documentation si nécessaire

#### 4. Tester

```bash
# Installer les dépendances de développement
pip install -r backend/requirements.txt

# Lancer les tests (si disponibles)
pytest

# Vérifier le formatage
black backend/ interface.py
flake8 backend/ interface.py
```

#### 5. Commit

Utilisez des messages de commit clairs et descriptifs :

```bash
git add .
git commit -m "feat: Ajout du support multi-langues"
```

Format recommandé :
- `feat:` Nouvelle fonctionnalité
- `fix:` Correction de bug
- `docs:` Documentation
- `style:` Formatage
- `refactor:` Refactoring
- `test:` Tests
- `chore:` Maintenance

#### 6. Push

```bash
git push origin feature/ma-nouvelle-fonctionnalite
```

#### 7. Ouvrir une Pull Request

1. Allez sur votre fork GitHub
2. Cliquez sur "New Pull Request"
3. Décrivez vos changements
4. Liez l'issue correspondante si applicable
5. Attendez la revue de code

## Standards de Code

### Python

- Suivre PEP 8
- Utiliser des type hints quand possible
- Maximum 100 caractères par ligne
- Docstrings en français
- Variables/fonctions en snake_case
- Classes en PascalCase

### Exemple

```python
def analyser_sentiment(texte: str) -> tuple[float, str]:
    """
    Analyse le sentiment d'un texte.
    
    Args:
        texte: Le texte à analyser
        
    Returns:
        tuple: (score, label) où score est entre -1 et 1
        et label est 'positif', 'neutre' ou 'négatif'
    """
    # Votre code ici
    pass
```

### Documentation

- Mettre à jour le README.md si nécessaire
- Documenter les nouvelles APIs
- Ajouter des exemples d'utilisation
- Inclure des captures d'écran pour l'UI

### Tests

- Ajouter des tests pour les nouvelles fonctionnalités
- Maintenir un coverage > 70%
- Tester les cas limites
- Tester les erreurs

## Structure des Commits

### Bon commit

```
feat: Ajout de la détection de langue

- Intégration du modèle langdetect
- Support de 50+ langues
- Mise à jour de la documentation
- Tests unitaires ajoutés
```

### Mauvais commit

```
fix stuff
```

## Revue de Code

Toutes les Pull Requests passent par une revue. Attendez-vous à :

- Des questions de clarification
- Des suggestions d'amélioration
- Des demandes de modifications
- Des tests supplémentaires

C'est un processus normal et constructif !

## Premiers Pas

Vous ne savez pas par où commencer ? Cherchez les issues avec les labels :

- `good first issue` : Parfait pour débuter
- `help wanted` : On a besoin d'aide
- `documentation` : Améliorer la doc

## Questions ?

N'hésitez pas à :
- Ouvrir une issue de discussion
- Demander des clarifications dans les PR
- Contacter les mainteneurs

Merci de contribuer à Nexus ! 🚀
