import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import faiss
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
import spacy
from collections import Counter
import pickle
import json
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from transformers import AutoTokenizer, AutoModel
import torch
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA

# Téléchargement des ressources NLTK
try:
    stop_words = set(stopwords.words('french'))
except:
    nltk.download('stopwords')
    nltk.download('punkt')
    stop_words = set(stopwords.words('french'))

class AdvancedIncidentSimilarity:
    """
    Système avancé de recherche de similarité pour incidents IT
    Utilise une approche hybride multi-modèles pour une précision maximale
    """
    
    def __init__(self, language='french'):
        self.language = language
        self.models = {}
        self.vectorizers = {}
        self.similarity_matrices = {}
        self.incident_embeddings = {}
        self.clustered_data = {}
        
        # Initialisation des modèles
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialise tous les modèles de similarité"""
        print("🚀 Initialisation des modèles avancés...")
        
        # 1. Modèle TF-IDF optimisé
        self.vectorizers['tfidf'] = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),  # Unigrams, bigrams, trigrams
            stop_words=list(stop_words),
            min_df=2,
            max_df=0.85,
            sublinear_tf=True,  # Améliore les performances
            use_idf=True
        )
        
        # 2. Modèle Sentence-BERT multilingue
        self.models['sbert'] = SentenceTransformer('distiluse-base-multilingual-cased')
        
        # 3. Modèle CamemBERT pour le français (si disponible)
        try:
            self.models['camembert_tokenizer'] = AutoTokenizer.from_pretrained('camembert-base')
            self.models['camembert_model'] = AutoModel.from_pretrained('camembert-base')
            print("✅ CamemBERT chargé avec succès")
        except:
            print("⚠️ CamemBERT non disponible, utilisation de SBERT uniquement")
        
        # 4. Stemmer français
        self.stemmer = SnowballStemmer('french')
        
        # 5. Index FAISS pour recherche ultra-rapide
        self.faiss_indices = {}
        
    def preprocess_text(self, text):
        """Préprocessing avancé du texte"""
        if pd.isna(text) or text == '':
            return ""
        
        # Conversion en minuscules
        text = str(text).lower()
        
        # Suppression des caractères spéciaux mais conservation des accents
        text = re.sub(r'[^\w\sàâäçéèêëïîôöùûüÿ-]', ' ', text)
        
        # Suppression des espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Tokenisation et suppression des mots vides
        words = word_tokenize(text, language='french')
        words = [self.stemmer.stem(word) for word in words 
                if word not in stop_words and len(word) > 2]
        
        return ' '.join(words)
    
    def extract_technical_features(self, text):
        """Extraction de caractéristiques techniques spécifiques IT"""
        features = {}
        
        # Codes d'erreur
        error_codes = re.findall(r'\b\d{3,4}\b|\berror\s*\d+\b', text.lower())
        features['error_codes'] = error_codes
        
        # Adresses IP
        ip_addresses = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
        features['ip_addresses'] = ip_addresses
        
        # Services/Applications courantes
        services = ['apache', 'nginx', 'mysql', 'postgresql', 'redis', 'mongodb', 
                   'docker', 'kubernetes', 'jenkins', 'tomcat', 'iis']
        found_services = [service for service in services if service in text.lower()]
        features['services'] = found_services
        
        # Systèmes d'exploitation
        os_keywords = ['windows', 'linux', 'ubuntu', 'centos', 'rhel', 'debian', 'macos']
        found_os = [os_name for os_name in os_keywords if os_name in text.lower()]
        features['operating_systems'] = found_os
        
        return features
    
    def fit_transform_tfidf(self, incidents_df):
        """Entraînement et transformation TF-IDF"""
        print("📊 Entraînement du modèle TF-IDF...")
        
        # Préprocessing
        processed_texts = incidents_df['description'].apply(self.preprocess_text)
        
        # Transformation TF-IDF
        tfidf_matrix = self.vectorizers['tfidf'].fit_transform(processed_texts)
        
        # Calcul de la matrice de similarité
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        self.incident_embeddings['tfidf'] = tfidf_matrix
        self.similarity_matrices['tfidf'] = similarity_matrix
        
        print(f"✅ TF-IDF: {tfidf_matrix.shape[0]} incidents, {tfidf_matrix.shape[1]} features")
        return tfidf_matrix
    
    def fit_transform_sbert(self, incidents_df):
        """Entraînement et transformation Sentence-BERT"""
        print("🧠 Génération des embeddings Sentence-BERT...")
        
        descriptions = incidents_df['description'].fillna('').tolist()
        
        # Génération des embeddings
        embeddings = self.models['sbert'].encode(descriptions, 
                                               batch_size=32, 
                                               show_progress_bar=True)
        
        # Calcul de la similarité cosinus
        similarity_matrix = cosine_similarity(embeddings)
        
        self.incident_embeddings['sbert'] = embeddings
        self.similarity_matrices['sbert'] = similarity_matrix
        
        # Création de l'index FAISS pour recherche rapide
        dimension = embeddings.shape[1]
        self.faiss_indices['sbert'] = faiss.IndexFlatIP(dimension)  # Inner Product
        
        # Normalisation pour utiliser cosine similarity avec inner product
        embeddings_normalized = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        self.faiss_indices['sbert'].add(embeddings_normalized.astype('float32'))
        
        print(f"✅ SBERT: {embeddings.shape[0]} incidents, {embeddings.shape[1]}D embeddings")
        return embeddings
    
    def create_hybrid_similarity(self, weights={'tfidf': 0.3, 'sbert': 0.7}):
        """Création d'une matrice de similarité hybride"""
        print("🔄 Création de la similarité hybride...")
        
        hybrid_matrix = np.zeros_like(self.similarity_matrices['tfidf'])
        
        for model_name, weight in weights.items():
            if model_name in self.similarity_matrices:
                hybrid_matrix += weight * self.similarity_matrices[model_name]
        
        self.similarity_matrices['hybrid'] = hybrid_matrix
        print(f"✅ Matrice hybride créée avec les poids: {weights}")
        
        return hybrid_matrix
    
    def find_similar_incidents(self, query_idx, method='hybrid', top_k=10, threshold=0.3):
        """Recherche des incidents similaires"""
        if method not in self.similarity_matrices:
            raise ValueError(f"Méthode {method} non disponible")
        
        similarities = self.similarity_matrices[method][query_idx]
        
        # Récupération des indices triés par similarité
        similar_indices = np.argsort(similarities)[::-1]
        
        # Filtrage par seuil et exclusion de l'incident lui-même
        filtered_indices = []
        filtered_scores = []
        
        for idx in similar_indices:
            if idx != query_idx and similarities[idx] > threshold:
                filtered_indices.append(idx)
                filtered_scores.append(similarities[idx])
                
                if len(filtered_indices) >= top_k:
                    break
        
        return filtered_indices, filtered_scores
    
    def search_by_text(self, query_text, method='sbert', top_k=10):
        """Recherche par texte libre"""
        if method == 'tfidf':
            # Préprocessing et vectorisation
            processed_query = self.preprocess_text(query_text)
            query_vector = self.vectorizers['tfidf'].transform([processed_query])
            
            # Calcul des similarités
            similarities = cosine_similarity(query_vector, self.incident_embeddings['tfidf']).flatten()
            
        elif method == 'sbert':
            # Génération de l'embedding
            query_embedding = self.models['sbert'].encode([query_text])
            query_normalized = query_embedding / np.linalg.norm(query_embedding)
            
            # Recherche avec FAISS
            scores, indices = self.faiss_indices['sbert'].search(
                query_normalized.astype('float32'), top_k
            )
            
            return indices[0], scores[0]
        
        # Pour TF-IDF, tri manuel
        top_indices = np.argsort(similarities)[::-1][:top_k]
        top_scores = similarities[top_indices]
        
        return top_indices, top_scores
    
    def perform_clustering(self, method='sbert', n_clusters=8):
        """Clustering des incidents pour identifier les patterns"""
        print(f"🎯 Clustering des incidents avec {method}...")
        
        if method == 'sbert':
            embeddings = self.incident_embeddings['sbert']
        else:
            embeddings = self.incident_embeddings['tfidf'].toarray()
        
        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)
        
        self.clustered_data[method] = {
            'labels': cluster_labels,
            'centroids': kmeans.cluster_centers_,
            'model': kmeans
        }
        
        print(f"✅ {n_clusters} clusters identifiés")
        return cluster_labels
    
    def visualize_similarity_network(self, incidents_df, method='sbert', threshold=0.7, max_nodes=50):
        """Visualisation réseau des similarités"""
        print("📊 Création du réseau de similarité...")
        
        # Sélection d'un sous-ensemble pour la visualisation
        if len(incidents_df) > max_nodes:
            sample_indices = np.random.choice(len(incidents_df), max_nodes, replace=False)
            df_sample = incidents_df.iloc[sample_indices].copy()
            similarity_sample = self.similarity_matrices[method][np.ix_(sample_indices, sample_indices)]
        else:
            df_sample = incidents_df.copy()
            similarity_sample = self.similarity_matrices[method]
        
        # Création des arêtes au-dessus du seuil
        edges = []
        edge_weights = []
        
        for i in range(len(df_sample)):
            for j in range(i+1, len(df_sample)):
                if similarity_sample[i, j] > threshold:
                    edges.append((i, j))
                    edge_weights.append(similarity_sample[i, j])
        
        print(f"✅ Réseau créé: {len(df_sample)} nœuds, {len(edges)} arêtes")
        
        return {
            'nodes': df_sample,
            'edges': edges,
            'weights': edge_weights,
            'similarity_matrix': similarity_sample
        }
    
    def create_similarity_heatmap(self, incidents_df, method='hybrid', sample_size=20):
        """Création d'une heatmap de similarité"""
        # Échantillonnage pour la visualisation
        if len(incidents_df) > sample_size:
            sample_indices = np.random.choice(len(incidents_df), sample_size, replace=False)
            sample_labels = [f"Incident_{i}" for i in sample_indices]
        else:
            sample_indices = range(len(incidents_df))
            sample_labels = [f"Incident_{i}" for i in sample_indices]
        
        similarity_sample = self.similarity_matrices[method][np.ix_(sample_indices, sample_indices)]
        
        # Création de la heatmap avec Plotly
        fig = go.Figure(data=go.Heatmap(
            z=similarity_sample,
            x=sample_labels,
            y=sample_labels,
            colorscale='Viridis',
            showscale=True
        ))
        
        fig.update_layout(
            title=f'Matrice de Similarité - Méthode: {method.upper()}',
            xaxis_title="Incidents",
            yaxis_title="Incidents",
            width=800,
            height=800
        )
        
        return fig
    
    def analyze_similarity_distribution(self, method='hybrid'):
        """Analyse de la distribution des scores de similarité"""
        similarity_matrix = self.similarity_matrices[method]
        
        # Extraction de la partie triangulaire supérieure (sans la diagonale)
        mask = np.triu(np.ones_like(similarity_matrix, dtype=bool), k=1)
        similarity_scores = similarity_matrix[mask]
        
        stats = {
            'mean': np.mean(similarity_scores),
            'median': np.median(similarity_scores),
            'std': np.std(similarity_scores),
            'min': np.min(similarity_scores),
            'max': np.max(similarity_scores),
            'q25': np.percentile(similarity_scores, 25),
            'q75': np.percentile(similarity_scores, 75)
        }
        
        return stats, similarity_scores
    
    def evaluate_similarity_quality(self, incidents_df, ground_truth_col=None):
        """Évaluation de la qualité des méthodes de similarité"""
        results = {}
        
        for method in self.similarity_matrices.keys():
            print(f"📈 Évaluation de {method}...")
            
            # Calculs de qualité
            similarity_matrix = self.similarity_matrices[method]
            
            # Diversité des scores
            mask = np.triu(np.ones_like(similarity_matrix, dtype=bool), k=1)
            scores = similarity_matrix[mask]
            
            # Métriques de qualité
            results[method] = {
                'score_range': np.max(scores) - np.min(scores),
                'score_variance': np.var(scores),
                'high_similarity_pairs': np.sum(scores > 0.8),
                'medium_similarity_pairs': np.sum((scores > 0.4) & (scores <= 0.8)),
                'low_similarity_pairs': np.sum(scores <= 0.4),
                'mean_similarity': np.mean(scores)
            }
        
        return results
    
    def save_model(self, filepath):
        """Sauvegarde du modèle complet"""
        model_data = {
            'vectorizers': self.vectorizers,
            'similarity_matrices': self.similarity_matrices,
            'incident_embeddings': self.incident_embeddings,
            'clustered_data': self.clustered_data
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Modèle sauvegardé: {filepath}")
    
    def load_model(self, filepath):
        """Chargement du modèle sauvegardé"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vectorizers = model_data['vectorizers']
        self.similarity_matrices = model_data['similarity_matrices']
        self.incident_embeddings = model_data['incident_embeddings'] 
        self.clustered_data = model_data['clustered_data']
        
        print(f"✅ Modèle chargé: {filepath}")


def create_demo_dataset():
    """Chargement d'un dataset d'incidents depuis data.csv structuré"""
    # Lecture du CSV avec en-tête
    df = pd.read_csv(r'c:\Users\MOHCINE_01\Desktop\incidents_management\backend\data.csv', encoding='utf-8')
    
    # Vérification des colonnes attendues
    required_cols = {'id_incident', 'date', 'description', 'priorité'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Le fichier CSV doit contenir les colonnes : {required_cols}")
    
    if df.empty:
        raise ValueError("Le fichier data.csv est vide.")
    if len(df) < 20:
        raise ValueError("Le fichier data.csv doit contenir au moins 20 incidents pour la démonstration.")
    
    # Création des colonnes supplémentaires aléatoires (optionnel)
    categories = ['Database', 'Web Server', 'Network', 'Application', 'Security', 'Infrastructure']
    
    df['category'] = np.random.choice(categories, len(df))
    df['resolved'] = np.random.choice([True, False], len(df), p=[0.8, 0.2])
    
    # Conversion de la date
    df['created_date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Nettoyage des colonnes
    df = df.rename(columns={'id_incident': 'id', 'priorité': 'priority'})
    
    return df



def main_demo():
    """Démonstration complète du système"""
    print("🎯 SYSTÈME AVANCÉ DE SIMILARITÉ POUR INCIDENTS IT")
    print("=" * 60)
    
    # 1. Création du dataset de démonstration
    print("\n1️⃣ Création du dataset de test...")
    incidents_df = create_demo_dataset()
    print(f"✅ Dataset créé: {len(incidents_df)} incidents")
    
    # 2. Initialisation du système
    print("\n2️⃣ Initialisation du système de similarité...")
    similarity_system = AdvancedIncidentSimilarity()
    
    # 3. Entraînement des modèles
    print("\n3️⃣ Entraînement des modèles...")
    similarity_system.fit_transform_tfidf(incidents_df)
    similarity_system.fit_transform_sbert(incidents_df)
    similarity_system.create_hybrid_similarity({'tfidf': 0.3, 'sbert': 0.7})
    
    # 4. Clustering
    print("\n4️⃣ Analyse par clustering...")
    clusters = similarity_system.perform_clustering(method='sbert', n_clusters=5)
    incidents_df['cluster'] = clusters
    
    # 5. Démonstration de recherche
    print("\n5️⃣ Démonstration de recherche de similarité...")
    
    # Recherche par incident existant
    query_idx = 0
    query_description = incidents_df.iloc[query_idx]['description']
    print(f"\n🔍 Recherche pour: '{query_description}'")
    
    similar_indices, similar_scores = similarity_system.find_similar_incidents(
        query_idx, method='hybrid', top_k=5
    )
    
    print("\n📋 Incidents similaires trouvés:")
    for i, (idx, score) in enumerate(zip(similar_indices, similar_scores)):
        print(f"{i+1}. Score: {score:.3f} - {incidents_df.iloc[idx]['description'][:80]}...")
    
    # Recherche par texte libre
    print(f"\n🔍 Recherche par texte libre: 'problème base de données'")
    search_indices, search_scores = similarity_system.search_by_text(
        "problème base de données", method='sbert', top_k=3
    )
    
    print("\n📋 Résultats de recherche:")
    for i, (idx, score) in enumerate(zip(search_indices, search_scores)):
        print(f"{i+1}. Score: {score:.3f} - {incidents_df.iloc[idx]['description'][:80]}...")
    
    # 6. Analyse de qualité
    print("\n6️⃣ Analyse de la qualité des méthodes...")
    quality_results = similarity_system.evaluate_similarity_quality(incidents_df)
    
    for method, metrics in quality_results.items():
        print(f"\n📊 Méthode {method.upper()}:")
        print(f"   Similarité moyenne: {metrics['mean_similarity']:.3f}")
        print(f"   Paires haute similarité (>0.8): {metrics['high_similarity_pairs']}")
        print(f"   Variance des scores: {metrics['score_variance']:.3f}")
    
    # 7. Statistiques de distribution
    print("\n7️⃣ Analyse de distribution des similarités...")
    for method in ['tfidf', 'sbert', 'hybrid']:
        stats, scores = similarity_system.analyze_similarity_distribution(method)
        print(f"\n📈 Distribution {method.upper()}:")
        print(f"   Moyenne: {stats['mean']:.3f} ± {stats['std']:.3f}")
        print(f"   Médiane: {stats['median']:.3f}")
        print(f"   Étendue: [{stats['min']:.3f}, {stats['max']:.3f}]")
    
    # 8. Sauvegarde
    print("\n8️⃣ Sauvegarde du modèle...")
    similarity_system.save_model('incident_similarity_model.pkl')
    
    print("\n✅ Démonstration terminée avec succès!")
    print("\n🎯 Fonctionnalités implémentées:")
    print("   ✓ Similarité TF-IDF avec preprocessing avancé")
    print("   ✓ Embeddings Sentence-BERT multilingues") 
    print("   ✓ Similarité hybride pondérée")
    print("   ✓ Recherche ultra-rapide avec FAISS")
    print("   ✓ Clustering automatique des incidents")
    print("   ✓ Recherche par texte libre")
    print("   ✓ Métriques de qualité détaillées")
    print("   ✓ Visualisations avancées")
    print("   ✓ Système de sauvegarde/chargement")
    
    return similarity_system, incidents_df


if __name__ == "__main__":
    # Exécution de la démonstration
    model, data = main_demo()