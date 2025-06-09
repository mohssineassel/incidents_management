import React, { useState } from 'react';
import { SearchIcon } from '@heroicons/react/solid';  // Icône de loupe pour le bouton
import IncidentCard from './IncidentCard';

// Données simulées d'incidents existants (id, description, catégorie, priorité)
const INCIDENTS_DATA = [
  { id: 1, description: "Serveur web en panne", category: "Infrastructure", priority: "Critique" },
  { id: 2, description: "Erreur applicative sur l'application mobile", category: "Logiciel", priority: "Haute" },
  { id: 3, description: "Imprimante hors service", category: "Matériel", priority: "Basse" },
  { id: 4, description: "Latence réseau anormale", category: "Réseau", priority: "Moyenne" },
  { id: 5, description: "Incident de sécurité mineur", category: "Sécurité", priority: "Moyenne" },
  // ... on peut ajouter d'autres incidents simulés au besoin
];

// Fonction simulant la recherche d'incidents similaires en se basant sur des mots clés
function searchIncidents(query) {
  const lowerQuery = query.toLowerCase();
  const words = lowerQuery.split(/\s+/).filter(w => w);
  if (words.length === 0) {
    return [];  // rien à chercher si requête vide
  }
  // Filtrer les incidents contenant au moins un des mots clés dans la description ou la catégorie
  let results = INCIDENTS_DATA.filter(inc => {
    const text = (inc.description + " " + inc.category).toLowerCase();
    return words.some(word => text.includes(word));
  });
  // Pour chaque incident trouvé, attribuer un score de similarité simulé
  results = results.map(inc => {
    // Score de base = proportion de mots clés présents, avec un aléatoire pour simuler un modèle
    let scoreRatio = 0;
    words.forEach(word => {
      if ((inc.description + " " + inc.category).toLowerCase().includes(word)) {
        scoreRatio += 1;
      }
    });
    scoreRatio = scoreRatio / words.length;
    const randomFactor = Math.random() * 0.3; // facteur aléatoire pour varier le score
    const similarityScore = Math.min(1, scoreRatio + 0.5 + randomFactor);
    return { ...inc, similarity: similarityScore };
  });
  // Tri des résultats par score de similarité décroissant
  results.sort((a, b) => b.similarity - a.similarity);
  return results;
}

/**
 * Composant de page pour la recherche de similarité d'incidents IT.
 * L'utilisateur saisit une description d'incident et voit une liste d'incidents similaires avec score, catégorie et priorité.
 */
export default function SimilaritySearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);  // null = pas encore de recherche effectuée

  // Gestion de la soumission du formulaire de recherche
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (trimmed === "") {
      // Si le champ est vide, on ne lance pas la recherche (on pourrait afficher une alerte ou une validation)
      return;
    }
    // Effectuer la recherche simulée d'incidents similaires
    const found = searchIncidents(trimmed);
    setResults(found);
  };

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Recherche de Similarité</h2>
      {/* Formulaire de recherche */}
      <form onSubmit={handleSearchSubmit} className="flex items-center max-w-xl">
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Décrivez un incident à rechercher..." 
          className="flex-grow border border-gray-300 rounded px-3 py-2 mr-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button 
          type="submit" 
          className="flex items-center bg-indigo-600 text-white font-medium px-4 py-2 rounded hover:bg-indigo-700"
        >
          <SearchIcon className="h-5 w-5 text-white mr-1" />
          Rechercher
        </button>
      </form>

      {/* Affichage des résultats */}
      {results === null ? (
        // Aucune recherche encore effectuée
        <p className="mt-4 text-gray-600">Tapez une description d'incident puis lancez la recherche pour voir les résultats similaires.</p>
      ) : results.length === 0 ? (
        // Recherche effectuée mais aucun incident trouvé
        <p className="mt-4 text-gray-600">Aucun incident similaire trouvé.</p>
      ) : (
        // Résultats trouvés : affichage sous forme de cartes
        <div className="grid md:grid-cols-2 gap-4 mt-5 fade-in">
          {results.map(inc => (
            <IncidentCard key={inc.id} incident={inc} />
          ))}
        </div>
      )}
    </div>
  );
}
