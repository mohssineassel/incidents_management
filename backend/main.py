from faiss_model import ajouter_incident, rechercher_incidents

# --- Ajouter des incidents ---
ajouter_incident("Erreur de connexion au serveur principal")
ajouter_incident("Problème d'accès à la base de données")
ajouter_incident("Incident critique sur le logiciel X")
ajouter_incident("Erreur de réseau dans l'application interne")

# --- Rechercher ---
print("\nRésultats de recherche :")
rechercher_incidents("Connexion à la base de données")
