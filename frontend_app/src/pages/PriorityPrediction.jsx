import React, { useState } from 'react';
import { CheckCircleIcon, ExclamationCircleIcon, ExclamationIcon, ShieldExclamationIcon } from '@heroicons/react/solid';

// Fonction simulant un modèle de prédiction de priorité à partir de la description.
// Détermine une priorité (Basse, Moyenne, Haute, Critique) en fonction de mots clés, et génère un score de confiance.
function simulatePriorityPrediction(description) {
  const text = description.toLowerCase();
  let priority = "Moyenne";
  let score = 0.6;
  if (text.includes("urgent") || text.includes("critique") || text.includes("panne") || text.includes("serveur down")) {
    priority = "Critique";
    score = 0.95;
  } else if (text.includes("important") || text.includes("haute") || text.includes("majeur")) {
    priority = "Haute";
    score = 0.8;
  } else if (text.includes("mineur") || text.includes("faible") || text.includes("amélioration")) {
    priority = "Basse";
    score = 0.3;
  }
  // (Note: la logique ci-dessus est simplifiée; un vrai modèle AI utiliserait des techniques NLP avancées)
  return { priority, score };
}

/**
 * Composant de page pour la prédiction automatique de la priorité d'un incident.
 * L'utilisateur entre une description, et le système affiche une priorité estimée avec un score de confiance.
 */
export default function PriorityPrediction() {
  const [description, setDescription] = useState("");
  const [prediction, setPrediction] = useState(null); // { priority: "...", score: 0.xx } ou null si pas encore de prédiction

  // Soumission du formulaire de prédiction
  const handlePredictSubmit = (e) => {
    e.preventDefault();
    if (!description.trim()) {
      return; // Si la description est vide, ne rien faire (on pourrait ajouter un message d'erreur)
    }
    // Appel au "modèle" simulé pour obtenir une priorité et un score
    const result = simulatePriorityPrediction(description);
    setPrediction(result);
  };

  // Préparation des éléments d'affichage en fonction de la priorité prédite
  let PriorityIcon = null;
  let containerClasses = "flex items-center p-4 rounded-md border-l-4";
  let iconClasses = "h-8 w-8 mr-3";
  let titleClasses = "text-xl font-bold";
  let infoColorClass = "text-gray-700";  // couleur du texte du score

  if (prediction) {
    // Configurer les styles et l'icône selon le niveau de priorité
    switch (prediction.priority) {
      case "Critique":
        PriorityIcon = ShieldExclamationIcon;
        containerClasses += " bg-red-50 border-red-600";
        iconClasses += " text-red-600";
        titleClasses += " text-red-700";
        break;
      case "Haute":
        PriorityIcon = ExclamationIcon;
        containerClasses += " bg-orange-50 border-orange-500";
        iconClasses += " text-orange-500";
        titleClasses += " text-orange-700";
        break;
      case "Moyenne":
        PriorityIcon = ExclamationCircleIcon;
        containerClasses += " bg-yellow-50 border-yellow-500";
        iconClasses += " text-yellow-500";
        titleClasses += " text-yellow-700";
        break;
      case "Basse":
        PriorityIcon = CheckCircleIcon;
        containerClasses += " bg-green-50 border-green-600";
        iconClasses += " text-green-600";
        titleClasses += " text-green-700";
        break;
      default:
        PriorityIcon = ExclamationCircleIcon;
        containerClasses += " bg-gray-50 border-gray-400";
        iconClasses += " text-gray-500";
        titleClasses += " text-gray-800";
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Prédiction & Priorisation</h2>
      {/* Formulaire de saisie de la description d'incident */}
      <form onSubmit={handlePredictSubmit} className="max-w-xl">
        <textarea 
          rows="4"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Décrivez brièvement le problème rencontré..." 
          className="w-full border border-gray-300 rounded px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button 
          type="submit" 
          className="mt-3 bg-indigo-600 text-white font-medium px-4 py-2 rounded hover:bg-indigo-700"
        >
          Prédire la priorité
        </button>
      </form>

      {/* Affichage du résultat de prédiction */}
      {prediction === null ? (
        // Aucune prédiction encore effectuée
        <p className="mt-4 text-gray-600">Entrez une description d'incident ci-dessus, puis cliquez sur "Prédire la priorité" pour obtenir une estimation.</p>
      ) : (
        // Résultat de la prédiction affiché dans une carte stylée
        <div className={`mt-5 ${containerClasses} fade-in`}>
          {PriorityIcon && <PriorityIcon className={iconClasses} />}
          <div>
            <h3 className={titleClasses}>Priorité {prediction.priority}</h3>
            <p className={infoColorClass}>
              Score de confiance : {Math.round(prediction.score * 100)}%
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
