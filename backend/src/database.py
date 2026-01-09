from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# On définit le nom du fichier de base de données
DATABASE_URL = "sqlite:///./nexis.db"

# Création du moteur
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Création de la Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# La classe de base
Base = declarative_base()

# Fonction utilitaire pour récupérer la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 👇 C'est cette fonction qui manquait !
def init_db():
    """Crée les tables de la base de données si elles n'existent pas."""
    # On importe le modèle ici pour être sûr qu'il est connu de SQLAlchemy
    from src.models import Article
    Base.metadata.create_all(bind=engine)