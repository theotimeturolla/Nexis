from src.database import engine, Base
from src.models import Article

print("🚧 Création de la base de données nexis.db en cours...")
Base.metadata.create_all(bind=engine)
print("✅ Base de données créée avec succès ! Le fichier 'nexis.db' est prêt.")