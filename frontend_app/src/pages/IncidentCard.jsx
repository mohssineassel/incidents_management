import React from 'react';

/**
 * Composant d'affichage d'un incident sous forme de carte.
 * Affiche la description, la catégorie, la priorité et le score de similarité (en pourcentage).
 * Les catégories et priorités sont présentées sous forme de badges colorés.
 */
export default function IncidentCard({ incident }) {
  const { description, category, priority, similarity } = incident;

  // Classes CSS Tailwind pour le badge de catégorie (couleur par catégorie, sinon gris par défaut)
  let categoryClass = "bg-gray-100 text-gray-800";
  if (category === "Infrastructure") categoryClass = "bg-blue-100 text-blue-800";
  else if (category === "Logiciel") categoryClass = "bg-purple-100 text-purple-800";
  else if (category === "Matériel") categoryClass = "bg-gray-100 text-gray-800";
  else if (category === "Réseau") categoryClass = "bg-teal-100 text-teal-800";
  else if (category === "Sécurité") categoryClass = "bg-pink-100 text-pink-800";

  // Classes CSS Tailwind pour le badge de priorité (couleur selon le niveau de priorité)
  let priorityClass = "bg-green-100 text-green-800";
  if (priority === "Moyenne") priorityClass = "bg-yellow-100 text-yellow-800";
  else if (priority === "Haute") priorityClass = "bg-orange-100 text-orange-800";
  else if (priority === "Critique") priorityClass = "bg-red-100 text-red-800";

  // Calcul du score de similarité en pourcentage (arrondi à l'entier)
  const similarityPercent = Math.round(similarity * 100);

  return (
    <div className="bg-white shadow rounded-lg p-4 hover:shadow-lg transition-shadow">
      {/* Description de l'incident */}
      <h4 className="text-sm font-semibold text-gray-800">
        {description}
      </h4>
      {/* Badges de catégorie, priorité et similarité */}
      <div className="flex items-center flex-wrap gap-2 mt-2">
        <span className={`${categoryClass} text-xs font-medium px-2 py-0.5 rounded`}>
          {category}
        </span>
        <span className={`${priorityClass} text-xs font-medium px-2 py-0.5 rounded`}>
          {priority}
        </span>
        <span className="bg-gray-200 text-gray-800 text-xs font-medium px-2 py-0.5 rounded">
          {similarityPercent}% similaire
        </span>
      </div>
    </div>
  );
}
