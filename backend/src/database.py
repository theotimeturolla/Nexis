from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# On définit le nom du fichier de base de données (ce sera un fichier local)
DATABASE_URL = "sqlite:///./nexis.db"

# Création du moteur (le cœur de la base de données)
# check_same_thread=False est nécessaire uniquement pour SQLite
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Création de la "Session" (l'outil qui permet d'écrire et lire)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# La classe de base pour tous nos modèles
Base = declarative_base()

# Fonction utilitaire pour récupérer la base de données proprement
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()