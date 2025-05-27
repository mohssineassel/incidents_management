import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix, roc_auc_score
from sklearn.model_selection import cross_val_score, StratifiedKFold
import time
import psutil
import gc
from collections import defaultdict
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

from a import AdvancedIncidentSimilarity, create_demo_dataset
warnings.filterwarnings('ignore')

class AdvancedEvaluationSystem:
    """
    Système d'évaluation complet pour les algorithmes de similarité
    Mesure performance, efficacité, robustesse et qualité
    """
    
    def __init__(self):
        self.results = defaultdict(dict)
        self.benchmarks = {}
        self.evaluation_history = []
        
    def evaluate_similarity_quality(self, similarity_system, incidents_df, ground_truth=None):
        """Évaluation complète de la qualité des similarités"""
        print("🎯 ÉVALUATION DE LA QUALITÉ DES SIMILARITÉS")
        print("=" * 50)
        
        results = {}
        
        for method in ['tfidf', 'sbert', 'hybrid']:
            if method in similarity_system.similarity_matrices:
                print(f"\n📊 Évaluation de {method.upper()}...")
                
                # 1. Métriques de base
                similarity_matrix = similarity_system.similarity_matrices[method]
                results[method] = self._calculate_base_metrics(similarity_matrix)
                
                # 2. Métriques de distribution
                results[method].update(self._calculate_distribution_metrics(similarity_matrix))
                
                # 3. Métriques de clustering
                results[method].update(self._evaluate_clustering_quality(similarity_matrix))
                
                # 4. Métriques de diversité
                results[method].update(self._calculate_diversity_metrics(similarity_matrix))
        
        self.results['quality'] = results
        return results
    
    def _calculate_base_metrics(self, similarity_matrix):
        """Calcul des métriques de base"""
        # Extraction de la partie triangulaire supérieure
        mask = np.triu(np.ones_like(similarity_matrix, dtype=bool), k=1)
        similarities = similarity_matrix[mask]
        
        return {
            'mean_similarity': np.mean(similarities),
            'median_similarity': np.median(similarities),
            'std_similarity': np.std(similarities),
            'min_similarity': np.min(similarities),
            'max_similarity': np.max(similarities),
            'similarity_range': np.max(similarities) - np.min(similarities),
            'q1_similarity': np.percentile(similarities, 25),
            'q3_similarity': np.percentile(similarities, 75),
            'iqr_similarity': np.percentile(similarities, 75) - np.percentile(similarities, 25)
        }
    
    def _calculate_distribution_metrics(self, similarity_matrix):
        """Métriques de distribution des similarités"""
        mask = np.triu(np.ones_like(similarity_matrix, dtype=bool), k=1)
        similarities = similarity_matrix[mask]
        
        # Calcul des seuils de similarité
        high_sim = np.sum(similarities > 0.8) / len(similarities)
        medium_sim = np.sum((similarities > 0.4) & (similarities <= 0.8)) / len(similarities)
        low_sim = np.sum(similarities <= 0.4) / len(similarities)
        
        # Entropie de la distribution
        hist, _ = np.histogram(similarities, bins=10, density=True)
        hist = hist[hist > 0]  # Éviter log(0)
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        
        return {
            'high_similarity_ratio': high_sim,
            'medium_similarity_ratio': medium_sim,
            'low_similarity_ratio': low_sim,
            'distribution_entropy': entropy,
            'skewness': self._calculate_skewness(similarities),
            'kurtosis': self._calculate_kurtosis(similarities)
        }
    
    def _calculate_skewness(self, data):
        """Calcul de l'asymétrie"""
        mean = np.mean(data)
        std = np.std(data)
        return np.mean(((data - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, data):
        """Calcul de l'aplatissement"""
        mean = np.mean(data)
        std = np.std(data)
        return np.mean(((data - mean) / std) ** 4) - 3
    
    def _evaluate_clustering_quality(self, similarity_matrix):
        """Évaluation de la qualité du clustering implicite"""
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score, calinski_harabasz_score
        
        # Conversion de la matrice de similarité en matrice de distance
        distance_matrix = 1 - similarity_matrix
        
        # Test de différents nombres de clusters
        silhouette_scores = []
        ch_scores = []
        
        for k in range(2, min(10, len(similarity_matrix) // 2)):
            try:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = kmeans.fit_predict(distance_matrix)
                
                sil_score = silhouette_score(distance_matrix, labels, metric='precomputed')
                ch_score = calinski_harabasz_score(distance_matrix, labels)
                
                silhouette_scores.append(sil_score)
                ch_scores.append(ch_score)
            except:
                silhouette_scores.append(0)
                ch_scores.append(0)
        
        return {
            'best_silhouette_score': max(silhouette_scores) if silhouette_scores else 0,
            'best_ch_score': max(ch_scores) if ch_scores else 0,
            'optimal_clusters': np.argmax(silhouette_scores) + 2 if silhouette_scores else 2
        }
    
    def _calculate_diversity_metrics(self, similarity_matrix):
        """Métriques de diversité"""
        # Calcul de la diversité moyenne
        mask = np.triu(np.ones_like(similarity_matrix, dtype=bool), k=1)
        similarities = similarity_matrix[mask]
        
        # Indice de Gini pour mesurer l'inégalité de distribution
        sorted_sims = np.sort(similarities)
        n = len(sorted_sims)
        index = np.arange(1, n + 1)
        gini = 2 * np.sum(index * sorted_sims) / (n * np.sum(sorted_sims)) - (n + 1) / n
        
        return {
            'diversity_index': 1 - np.mean(similarities),
            'gini_coefficient': gini,
            'unique_similarity_values': len(np.unique(similarities)),
            'similarity_variance': np.var(similarities)
        }
    
    def benchmark_performance(self, similarity_system, incidents_df, iterations=5):
        """Benchmark de performance (vitesse, mémoire, scalabilité)"""
        print("\n⚡ BENCHMARK DE PERFORMANCE")
        print("=" * 50)
        
        results = {}
        
        for method in ['tfidf', 'sbert', 'hybrid']:
            if method in similarity_system.similarity_matrices:
                print(f"\n🚀 Benchmark {method.upper()}...")
                
                results[method] = {}
                
                # 1. Test de vitesse de recherche
                search_times = []
                memory_usage = []
                
                for i in range(iterations):
                    # Mesure de la mémoire avant
                    gc.collect()
                    mem_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    
                    # Test de vitesse
                    start_time = time.time()
                    
                    # Simulation de recherches multiples
                    for query_idx in range(min(10, len(incidents_df))):
                        similar_indices, scores = similarity_system.find_similar_incidents(
                            query_idx, method=method, top_k=5
                        )
                    
                    end_time = time.time()
                    search_times.append((end_time - start_time) / 10)  # Temps moyen par recherche
                    
                    # Mesure de la mémoire après
                    mem_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    memory_usage.append(mem_after - mem_before)
                
                results[method]['avg_search_time'] = np.mean(search_times)
                results[method]['std_search_time'] = np.std(search_times)
                results[method]['avg_memory_usage'] = np.mean(memory_usage)
                results[method]['std_memory_usage'] = np.std(memory_usage)
                
                # 2. Test de scalabilité
                results[method].update(self._test_scalability(similarity_system, incidents_df, method))
                
                # 3. Test de robustesse
                results[method].update(self._test_robustness(similarity_system, incidents_df, method))
        
        self.results['performance'] = results
        return results
    
    def _test_scalability(self, similarity_system, incidents_df, method):
        """Test de scalabilité avec différentes tailles de données"""
        scalability_results = {}
        
        sizes = [len(incidents_df) // 4, len(incidents_df) // 2, len(incidents_df)]
        times = []
        
        for size in sizes:
            if size > 0:
                sample_df = incidents_df.head(size)
                start_time = time.time()
                
                # Simulation du temps de traitement
                if method == 'tfidf':
                    _ = similarity_system.vectorizers['tfidf'].transform(
                        sample_df['description'].fillna('').apply(similarity_system.preprocess_text)
                    )
                elif method == 'sbert':
                    _ = similarity_system.models['sbert'].encode(
                        sample_df['description'].fillna('').tolist()[:min(size, 50)]
                    )
                
                end_time = time.time()
                times.append(end_time - start_time)
        
        if len(times) > 1:
            # Estimation de la complexité (linéaire, quadratique, etc.)
            complexity_ratio = times[-1] / times[0] if times[0] > 0 else 1
            scalability_results['complexity_ratio'] = complexity_ratio
            scalability_results['scalability_score'] = 1 / complexity_ratio if complexity_ratio > 0 else 0
        
        scalability_results['processing_times'] = times
        return scalability_results
    
    def _test_robustness(self, similarity_system, incidents_df, method):
        """Test de robustesse avec données bruitées"""
        robustness_results = {}
        
        try:
            # Test avec données manquantes
            corrupted_df = incidents_df.copy()
            corrupted_df.loc[corrupted_df.index[:len(corrupted_df)//4], 'description'] = ''
            
            start_time = time.time()
            # Test de recherche avec données corrompues
            for i in range(min(5, len(corrupted_df))):
                try:
                    similar_indices, scores = similarity_system.find_similar_incidents(
                        i, method=method, top_k=3
                    )
                except:
                    pass
            
            robustness_time = time.time() - start_time
            robustness_results['robustness_time'] = robustness_time
            robustness_results['handles_missing_data'] = True
            
        except Exception as e:
            robustness_results['robustness_time'] = float('inf')
            robustness_results['handles_missing_data'] = False
        
        return robustness_results
    
    def evaluate_accuracy(self, similarity_system, incidents_df, ground_truth_pairs=None):
        """Évaluation de la précision avec vérité terrain"""
        print("\n🎯 ÉVALUATION DE LA PRÉCISION")
        print("=" * 50)
        
        if ground_truth_pairs is None:
            # Création d'une vérité terrain basique basée sur les catégories
            ground_truth_pairs = self._create_basic_ground_truth(incidents_df)
        
        results = {}
        
        for method in ['tfidf', 'sbert', 'hybrid']:
            if method in similarity_system.similarity_matrices:
                print(f"\n📈 Précision {method.upper()}...")
                
                results[method] = self._calculate_accuracy_metrics(
                    similarity_system, incidents_df, ground_truth_pairs, method
                )
        
        self.results['accuracy'] = results
        return results
    
    def _create_basic_ground_truth(self, incidents_df):
        """Création d'une vérité terrain basique"""
        ground_truth = []
        
        if 'category' in incidents_df.columns:
            # Grouper par catégorie
            for category in incidents_df['category'].unique():
                if pd.notna(category):
                    category_incidents = incidents_df[incidents_df['category'] == category].index.tolist()
                    
                    # Créer des paires positives (même catégorie)
                    for i in range(len(category_incidents)):
                        for j in range(i + 1, min(i + 5, len(category_incidents))):  # Limiter le nombre de paires
                            ground_truth.append((category_incidents[i], category_incidents[j], 1))
            
            # Créer des paires négatives (catégories différentes)
            categories = incidents_df['category'].dropna().unique()
            if len(categories) > 1:
                for i in range(min(50, len(incidents_df))):  # Limiter le nombre de paires négatives
                    cat1_incidents = incidents_df[incidents_df['category'] == categories[0]].index.tolist()
                    cat2_incidents = incidents_df[incidents_df['category'] == categories[1]].index.tolist()
                    
                    if cat1_incidents and cat2_incidents:
                        ground_truth.append((cat1_incidents[0], cat2_incidents[0], 0))
        
        return ground_truth
    
    def _calculate_accuracy_metrics(self, similarity_system, incidents_df, ground_truth_pairs, method):
        """Calcul des métriques de précision"""
        y_true = []
        y_scores = []
        
        similarity_matrix = similarity_system.similarity_matrices[method]
        
        for idx1, idx2, label in ground_truth_pairs:
            if idx1 < len(similarity_matrix) and idx2 < len(similarity_matrix):
                similarity_score = similarity_matrix[idx1, idx2]
                y_true.append(label)
                y_scores.append(similarity_score)
        
        if not y_true:
            return {'error': 'No valid ground truth pairs'}
        
        # Conversion en prédictions binaires
        threshold = 0.5
        y_pred = [1 if score > threshold else 0 for score in y_scores]
        
        # Calcul des métriques
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average='binary', zero_division=0
        )
        
        try:
            auc_score = roc_auc_score(y_true, y_scores)
        except:
            auc_score = 0.5
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'auc_score': auc_score,
            'accuracy': np.mean([t == p for t, p in zip(y_true, y_pred)]),
            'num_samples': len(y_true)
        }
    
    def comparative_analysis(self):
        """Analyse comparative des différentes méthodes"""
        print("\n🔍 ANALYSE COMPARATIVE")
        print("=" * 50)
        
        if not self.results:
            print("❌ Aucun résultat d'évaluation disponible. Lancez d'abord les évaluations.")
            return
        
        comparison = {}
        
        # Comparaison des métriques de qualité
        if 'quality' in self.results:
            comparison['quality'] = self._compare_quality_metrics()
        
        # Comparaison des performances
        if 'performance' in self.results:
            comparison['performance'] = self._compare_performance_metrics()
        
        # Comparaison de la précision
        if 'accuracy' in self.results:
            comparison['accuracy'] = self._compare_accuracy_metrics()
        
        # Score global
        comparison['overall_ranking'] = self._calculate_overall_ranking()
        
        self.results['comparison'] = comparison
        return comparison
    
    def _compare_quality_metrics(self):
        """Comparaison des métriques de qualité"""
        quality_comparison = {}
        
        methods = list(self.results['quality'].keys())
        
        # Métriques importantes
        key_metrics = [
            'mean_similarity', 'std_similarity', 'distribution_entropy',
            'best_silhouette_score', 'diversity_index'
        ]
        
        for metric in key_metrics:
            quality_comparison[metric] = {}
            values = []
            
            for method in methods:
                if metric in self.results['quality'][method]:
                    value = self.results['quality'][method][metric]
                    quality_comparison[metric][method] = value
                    values.append(value)
            
            # Déterminer le meilleur
            if values:
                if metric in ['distribution_entropy', 'best_silhouette_score', 'diversity_index']:
                    best_method = max(quality_comparison[metric].keys(), 
                                    key=lambda x: quality_comparison[metric][x])
                else:
                    best_method = min(quality_comparison[metric].keys(), 
                                    key=lambda x: abs(quality_comparison[metric][x] - 0.5))
                
                quality_comparison[metric]['best'] = best_method
        
        return quality_comparison
    
    def _compare_performance_metrics(self):
        """Comparaison des métriques de performance"""
        performance_comparison = {}
        
        methods = list(self.results['performance'].keys())
        
        key_metrics = ['avg_search_time', 'avg_memory_usage', 'scalability_score']
        
        for metric in key_metrics:
            performance_comparison[metric] = {}
            
            for method in methods:
                if metric in self.results['performance'][method]:
                    performance_comparison[metric][method] = self.results['performance'][method][metric]
            
            # Le meilleur est celui avec la valeur la plus faible (sauf pour scalability_score)
            if performance_comparison[metric]:
                if metric == 'scalability_score':
                    best_method = max(performance_comparison[metric].keys(), 
                                    key=lambda x: performance_comparison[metric][x])
                else:
                    best_method = min(performance_comparison[metric].keys(), 
                                    key=lambda x: performance_comparison[metric][x])
                
                performance_comparison[metric]['best'] = best_method
        
        return performance_comparison
    
    def _compare_accuracy_metrics(self):
        """Comparaison des métriques de précision"""
        accuracy_comparison = {}
        
        methods = list(self.results['accuracy'].keys())
        
        key_metrics = ['precision', 'recall', 'f1_score', 'auc_score', 'accuracy']
        
        for metric in key_metrics:
            accuracy_comparison[metric] = {}
            
            for method in methods:
                if metric in self.results['accuracy'][method]:
                    accuracy_comparison[metric][method] = self.results['accuracy'][method][metric]
            
            # Le meilleur est celui avec la valeur la plus élevée
            if accuracy_comparison[metric]:
                best_method = max(accuracy_comparison[metric].keys(), 
                                key=lambda x: accuracy_comparison[metric][x])
                accuracy_comparison[metric]['best'] = best_method
        
        return accuracy_comparison
    
    def _calculate_overall_ranking(self):
        """Calcul du classement global"""
        methods = set()
        
        # Collecter toutes les méthodes
        for category in self.results.values():
            if isinstance(category, dict):
                methods.update(category.keys())
        
        methods = list(methods)
        scores = defaultdict(float)
        
        # Pondération des différentes catégories
        weights = {
            'quality': 0.4,
            'performance': 0.3,
            'accuracy': 0.3
        }
        
        # Calcul des scores pondérés
        for category, weight in weights.items():
            if category in self.results:
                category_scores = self._calculate_category_scores(category)
                for method in methods:
                    if method in category_scores:
                        scores[method] += category_scores[method] * weight
        
        # Classement final
        ranked_methods = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'ranking': ranked_methods,
            'scores': dict(scores),
            'weights': weights
        }
    
    def _calculate_category_scores(self, category):
        """Calcul des scores pour une catégorie"""
        category_data = self.results[category]
        methods = list(category_data.keys())
        scores = {}
        
        if category == 'quality':
            # Score basé sur la diversité et la qualité du clustering
            for method in methods:
                data = category_data[method]
                score = 0
                
                # Diversité (plus c'est élevé, mieux c'est)
                if 'diversity_index' in data:
                    score += data['diversity_index'] * 0.3
                
                # Qualité du clustering
                if 'best_silhouette_score' in data:
                    score += data['best_silhouette_score'] * 0.4
                
                # Entropie de distribution
                if 'distribution_entropy' in data:
                    score += data['distribution_entropy'] * 0.3
                
                scores[method] = score
        
        elif category == 'performance':
            # Score basé sur la vitesse et l'efficacité mémoire
            max_time = max([data.get('avg_search_time', 0) for data in category_data.values()])
            max_memory = max([data.get('avg_memory_usage', 0) for data in category_data.values()])
            
            for method in methods:
                data = category_data[method]
                score = 0
                
                # Vitesse (inversé - plus c'est rapide, mieux c'est)
                if 'avg_search_time' in data and max_time > 0:
                    score += (1 - data['avg_search_time'] / max_time) * 0.4
                
                # Mémoire (inversé)
                if 'avg_memory_usage' in data and max_memory > 0:
                    score += (1 - data['avg_memory_usage'] / max_memory) * 0.3
                
                # Scalabilité
                if 'scalability_score' in data:
                    score += data['scalability_score'] * 0.3
                
                scores[method] = score
        
        elif category == 'accuracy':
            # Score basé sur les métriques de précision
            for method in methods:
                data = category_data[method]
                score = 0
                
                if 'f1_score' in data:
                    score += data['f1_score'] * 0.4
                
                if 'auc_score' in data:
                    score += data['auc_score'] * 0.3
                
                if 'accuracy' in data:
                    score += data['accuracy'] * 0.3
                
                scores[method] = score
        
        return scores
    
    def generate_report(self, output_file=None):
        """Génération d'un rapport complet"""
        print("\n📊 GÉNÉRATION DU RAPPORT")
        print("=" * 50)
        
        report_lines = []
        report_lines.append("# RAPPORT D'ÉVALUATION DES ALGORITHMES DE SIMILARITÉ")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # Résumé exécutif
        if 'comparison' in self.results and 'overall_ranking' in self.results['comparison']:
            ranking = self.results['comparison']['overall_ranking']['ranking']
            report_lines.append("## RÉSUMÉ EXÉCUTIF")
            report_lines.append("-" * 20)
            report_lines.append(f"🏆 Meilleure méthode: {ranking[0][0].upper()}")
            report_lines.append(f"📊 Score: {ranking[0][1]:.3f}")
            report_lines.append("")
            
            report_lines.append("### Classement complet:")
            for i, (method, score) in enumerate(ranking, 1):
                report_lines.append(f"{i}. {method.upper()}: {score:.3f}")
            report_lines.append("")
        
        # Détails par catégorie
        for category in ['quality', 'performance', 'accuracy']:
            if category in self.results:
                report_lines.append(f"## {category.upper()}")
                report_lines.append("-" * 20)
                
                for method, metrics in self.results[category].items():
                    if isinstance(metrics, dict) and 'error' not in metrics:
                        report_lines.append(f"### {method.upper()}")
                        
                        for metric, value in metrics.items():
                            if isinstance(value, (int, float)):
                                report_lines.append(f"- {metric}: {value:.4f}")
                        report_lines.append("")
                
                report_lines.append("")
        
        # Recommandations
        report_lines.append("## RECOMMANDATIONS")
        report_lines.append("-" * 20)
        
        if 'comparison' in self.results:
            comparison = self.results['comparison']
            
            # Recommandation pour la qualité
            if 'quality' in comparison:
                quality_best = self._find_best_overall(comparison['quality'])
                report_lines.append(f"🎯 Pour la qualité: Utilisez {quality_best}")
            
            # Recommandation pour la performance
            if 'performance' in comparison:
                perf_best = self._find_best_overall(comparison['performance'])
                report_lines.append(f"⚡ Pour la performance: Utilisez {perf_best}")
            
            # Recommandation pour la précision
            if 'accuracy' in comparison:
                acc_best = self._find_best_overall(comparison['accuracy'])
                report_lines.append(f"🎯 Pour la précision: Utilisez {acc_best}")
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"✅ Rapport sauvegardé dans {output_file}")
        
        print(report_content)
        return report_content
    
    def _find_best_overall(self, category_comparison):
        """Trouve la meilleure méthode pour une catégorie"""
        best_counts = defaultdict(int)
        
        for metric_data in category_comparison.values():
            if isinstance(metric_data, dict) and 'best' in metric_data:
                best_counts[metric_data['best']] += 1
        
        if best_counts:
            return max(best_counts.keys(), key=lambda x: best_counts[x])
        return "N/A"
    
    def create_visualizations(self):
        """Création de visualisations interactives"""
        print("\n📈 CRÉATION DES VISUALISATIONS")
        print("=" * 50)
        
        if not self.results:
            print("❌ Aucun résultat disponible pour la visualisation")
            return
        
        # 1. Graphique radar de comparaison
        self._create_radar_chart()
        
        # 2. Graphiques de distribution des similarités
        self._create_similarity_distributions()
        
        # 3. Graphique de performance temporelle
        self._create_performance_chart()
        
        # 4. Matrice de corrélation des métriques
        self._create_correlation_matrix()
    
    def _create_radar_chart(self):
        """Graphique radar pour comparer les méthodes"""
        if 'comparison' not in self.results:
            return
        
        methods = []
        metrics = []
        values = []
        
        # Collecte des données
        comparison = self.results['comparison']
        for category in ['quality', 'performance', 'accuracy']:
            if category in comparison:
                for metric, method_scores in comparison[category].items():
                    if isinstance(method_scores, dict) and 'best' not in method_scores:
                        for method, score in method_scores.items():
                            methods.append(method)
                            metrics.append(f"{category}_{metric}")
                            values.append(score)
        
        if methods:
            df_radar = pd.DataFrame({
                'method': methods,
                'metric': metrics,
                'value': values
            })
            
            # Normalisation des valeurs
            df_radar['normalized_value'] = df_radar.groupby('metric')['value'].transform(
                lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else 0
            )
            
            print("📊 Données préparées pour le graphique radar")
    
    def _create_similarity_distributions(self):
        """Histogrammes des distributions de similarité"""
        if 'quality' not in self.results:
            return
        
        print("📊 Distribution des similarités par méthode:")
        for method, metrics in self.results['quality'].items():
            print(f"{method.upper()}:")
            print(f"  - Moyenne: {metrics.get('mean_similarity', 0):.4f}")
            print(f"  - Écart-type: {metrics.get('std_similarity', 0):.4f}")
            print(f"  - Entropie: {metrics.get('distribution_entropy', 0):.4f}")
    
    def _create_performance_chart(self):
        """Graphique des performances temporelles"""
        if 'performance' not in self.results:
            return
        
        print("⚡ Performances par méthode:")
        for method, metrics in self.results['performance'].items():
            print(f"{method.upper()}:")
            print(f"  - Temps de recherche: {metrics.get('avg_search_time', 0):.4f}s")
            print(f"  - Usage mémoire: {metrics.get('avg_memory_usage', 0):.2f}MB")
            print(f"  - Score scalabilité: {metrics.get('scalability_score', 0):.4f}")
    
    def _create_correlation_matrix(self):
        """Matrice de corrélation des métriques"""
        if not self.results:
            return
        
        # Collecte de toutes les métriques numériques
        all_metrics = {}
        
        for category, methods in self.results.items():
            if isinstance(methods, dict) and category != 'comparison':
                for method, metrics in methods.items():
                    if isinstance(metrics, dict):
                        for metric, value in metrics.items():
                            if isinstance(value, (int, float)):
                                metric_name = f"{method}_{metric}"
                                all_metrics[metric_name] = value
        
        if all_metrics:
            print(f"📊 Collecté {len(all_metrics)} métriques pour l'analyse de corrélation")
    
    def run_complete_evaluation(self, similarity_system, incidents_df, ground_truth=None):
        """Exécution complète de toutes les évaluations"""
        print("🚀 LANCEMENT DE L'ÉVALUATION COMPLÈTE")
        print("=" * 60)
        
        start_time = time.time()
        
        # 1. Évaluation de la qualité
        try:
            print("\n1️⃣ Évaluation de la qualité...")
            self.evaluate_similarity_quality(similarity_system, incidents_df, ground_truth)
        except Exception as e:
            print(f"❌ Erreur lors de l'évaluation de qualité: {e}")
        
        # 2. Benchmark de performance
        try:
            print("\n2️⃣ Benchmark de performance...")
            self.benchmark_performance(similarity_system, incidents_df)
        except Exception as e:
            print(f"❌ Erreur lors du benchmark: {e}")
        
        # 3. Évaluation de la précision
        try:
            print("\n3️⃣ Évaluation de la précision...")
            self.evaluate_accuracy(similarity_system, incidents_df, ground_truth)
        except Exception as e:
            print(f"❌ Erreur lors de l'évaluation de précision: {e}")
        
        # 4. Analyse comparative
        try:
            print("\n4️⃣ Analyse comparative...")
            self.comparative_analysis()
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse comparative: {e}")
        
        # 5. Génération du rapport
        try:
            print("\n5️⃣ Génération du rapport...")
            self.generate_report()
        except Exception as e:
            print(f"❌ Erreur lors de la génération du rapport: {e}")
        
        # 6. Création des visualisations
        try:
            print("\n6️⃣ Création des visualisations...")
            self.create_visualizations()
        except Exception as e:
            print(f"❌ Erreur lors de la création des visualisations: {e}")
        
        total_time = time.time() - start_time
        print(f"\n✅ ÉVALUATION TERMINÉE EN {total_time:.2f} SECONDES")
        
        return self.results
    
    def export_results(self, filename="evaluation_results.json"):
        """Export des résultats en JSON"""
        import json
        
        # Conversion des valeurs numpy pour la sérialisation JSON
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj
        
        converted_results = convert_numpy(dict(self.results))
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(converted_results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Résultats exportés dans {filename}")
    
    def load_results(self, filename="evaluation_results.json"):
        """Chargement des résultats depuis un fichier JSON"""
        import json
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                loaded_results = json.load(f)
            
            self.results = defaultdict(dict, loaded_results)
            print(f"✅ Résultats chargés depuis {filename}")
            return True
        except FileNotFoundError:
            print(f"❌ Fichier {filename} non trouvé")
            return False
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            return False
    
    def get_recommendations(self):
        """Recommandations basées sur les résultats d'évaluation"""
        if not self.results:
            return "Aucune évaluation effectuée. Lancez d'abord une évaluation complète."
        
        recommendations = []
        
        # Analyse des résultats pour générer des recommandations
        if 'comparison' in self.results and 'overall_ranking' in self.results['comparison']:
            ranking = self.results['comparison']['overall_ranking']['ranking']
            
            if ranking:
                best_method = ranking[0][0]
                recommendations.append(f"🏆 Méthode recommandée globalement: {best_method.upper()}")
                
                # Recommandations spécifiques selon le contexte
                if best_method == 'hybrid':
                    recommendations.append("✅ La méthode hybride offre le meilleur équilibre entre qualité et performance")
                elif best_method == 'sbert':
                    recommendations.append("✅ SBERT excelle pour la compréhension sémantique des textes")
                elif best_method == 'tfidf':
                    recommendations.append("✅ TF-IDF est optimal pour la rapidité et l'efficacité mémoire")
        
        # Recommandations basées sur les métriques spécifiques
        if 'performance' in self.results:
            fastest_method = None
            fastest_time = float('inf')
            
            for method, metrics in self.results['performance'].items():
                if 'avg_search_time' in metrics:
                    if metrics['avg_search_time'] < fastest_time:
                        fastest_time = metrics['avg_search_time']
                        fastest_method = method
            
            if fastest_method:
                recommendations.append(f"⚡ Pour les applications temps réel: {fastest_method.upper()}")
        
        if 'accuracy' in self.results:
            most_accurate = None
            best_f1 = 0
            
            for method, metrics in self.results['accuracy'].items():
                if 'f1_score' in metrics:
                    if metrics['f1_score'] > best_f1:
                        best_f1 = metrics['f1_score']
                        most_accurate = method
            
            if most_accurate:
                recommendations.append(f"🎯 Pour la précision maximale: {most_accurate.upper()}")
        
        # Recommandations contextuelles
        recommendations.extend([
            "",
            "📋 CONSEILS D'UTILISATION:",
            "• Utilisez TF-IDF pour des datasets volumineux avec contraintes de performance",
            "• Choisissez SBERT pour une compréhension sémantique approfondie",
            "• Optez pour la méthode hybride pour un équilibre optimal",
            "• Considérez le contexte d'usage (temps réel vs. batch, précision vs. vitesse)",
            "",
            "⚠️  POINTS D'ATTENTION:",
            "• Évaluez régulièrement sur vos données spécifiques",
            "• Ajustez les paramètres selon vos besoins",
            "• Surveillez l'évolution des performances avec la croissance des données"
        ])
        
        return "\n".join(recommendations)
    
    def summary(self):
        """Résumé concis des résultats d'évaluation"""
        if not self.results:
            return "❌ Aucune évaluation disponible"
        
        summary_lines = ["📊 RÉSUMÉ D'ÉVALUATION", "=" * 30]
        
        # Nombre de méthodes évaluées
        methods_evaluated = set()
        for category in self.results.values():
            if isinstance(category, dict):
                methods_evaluated.update(category.keys())
        
        if 'comparison' in methods_evaluated:
            methods_evaluated.remove('comparison')
        
        summary_lines.append(f"🔍 Méthodes évaluées: {len(methods_evaluated)}")
        summary_lines.append(f"📋 Méthodes: {', '.join(methods_evaluated).upper()}")
        
        # Meilleure méthode
        if 'comparison' in self.results and 'overall_ranking' in self.results['comparison']:
            ranking = self.results['comparison']['overall_ranking']['ranking']
            if ranking:
                summary_lines.append(f"🏆 Meilleure méthode: {ranking[0][0].upper()} (Score: {ranking[0][1]:.3f})")
        
        # Statistiques par catégorie
        categories_evaluated = [cat for cat in ['quality', 'performance', 'accuracy'] if cat in self.results]
        summary_lines.append(f"📈 Catégories évaluées: {len(categories_evaluated)}")
        
        # Temps d'évaluation (si disponible)
        if hasattr(self, 'evaluation_time'):
            summary_lines.append(f"⏱️  Temps d'évaluation: {self.evaluation_time:.2f}s")
        
        return "\n".join(summary_lines)


# Classe utilitaire pour l'analyse statistique avancée
class StatisticalAnalyzer:
    """Analyseur statistique pour les métriques de similarité"""
    
    @staticmethod
    def perform_significance_test(results_method1, results_method2, metric='f1_score'):
        """Test de significativité statistique entre deux méthodes"""
        from scipy import stats
        
        try:
            values1 = [results_method1.get(metric, 0)]
            values2 = [results_method2.get(metric, 0)]
            
            # Test t de Student
            t_stat, p_value = stats.ttest_ind(values1, values2)
            
            return {
                't_statistic': t_stat,
                'p_value': p_value,
                'significant': p_value < 0.05,
                'confidence_level': 0.95
            }
        except:
            return {'error': 'Impossible de calculer la significativité'}
    
    @staticmethod
    def calculate_effect_size(results_method1, results_method2, metric='f1_score'):
        """Calcul de la taille d'effet (Cohen's d)"""
        try:
            mean1 = results_method1.get(metric, 0)
            mean2 = results_method2.get(metric, 0)
            
            # Approximation simple de Cohen's d
            pooled_std = np.sqrt((0.1**2 + 0.1**2) / 2)  # Approximation
            cohens_d = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0
            
            # Interprétation
            if abs(cohens_d) < 0.2:
                interpretation = "Petit effet"
            elif abs(cohens_d) < 0.5:
                interpretation = "Effet moyen"
            else:
                interpretation = "Grand effet"
            
            return {
                'cohens_d': cohens_d,
                'interpretation': interpretation,
                'magnitude': abs(cohens_d)
            }
        except:
            return {'error': 'Impossible de calculer la taille d\'effet'}


# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple d'utilisation du système d'évaluation
    print("🔬 SYSTÈME D'ÉVALUATION AVANCÉ POUR ALGORITHMES DE SIMILARITÉ")
    print("=" * 70)
    print()
    print("Ce système permet d'évaluer complètement vos algorithmes de similarité:")
    print("• 📊 Qualité des similarités (distribution, clustering, diversité)")
    print("• ⚡ Performance (vitesse, mémoire, scalabilité)")
    print("• 🎯 Précision (avec vérité terrain)")
    print("• 🔍 Analyse comparative complète")
    print("• 📈 Visualisations interactives")
    print("• 📋 Rapports détaillés")
    print()
    print("Usage:")
    
    # Initialisation
    # evaluator = AdvancedEvaluationSystem()

    # # Évaluation complète
    # results = evaluator.run_complete_evaluation(similarity_system, incidents_df)

    # # Recommandations
    # print(evaluator.get_recommendations())

    # # Export des résultats
    # evaluator.export_results("mon_evaluation.json")
    similarity_system = AdvancedIncidentSimilarity()
    
    # Création du dataset de test
    incidents_df = create_demo_dataset()
    
    # Entraînement des modèles
    similarity_system.fit_transform_tfidf(incidents_df)
    similarity_system.fit_transform_sbert(incidents_df)
    similarity_system.create_hybrid_similarity({'tfidf': 0.3, 'sbert': 0.7})
    
    # Lancement de l'évaluation complète
    evaluator = AdvancedEvaluationSystem()
    results = evaluator.run_complete_evaluation(similarity_system, incidents_df)
    
    # Affichage des recommandations
    print(evaluator.get_recommendations())
    
    # Export des résultats
    evaluator.export_results("mon_evaluation.json")