import React from 'react';
import { NavLink, Routes, Route } from 'react-router-dom';
import SimilaritySearch from './pages/SimilaritySearch';
import PriorityPrediction from './pages/PriorityPrediction';

// En-tête de navigation principal
function Header() {
  return (
    <nav className="bg-gray-800 text-white">
      <div className="container mx-auto flex justify-between items-center p-4">
        {/* Titre/branding du site */}
        <span className="text-lg font-bold">Gestion Incidents IT</span>
        {/* Liens de navigation */}
        <div className="flex space-x-4">
          <NavLink 
            to="/" 
            end 
            className={({ isActive }) => 
              isActive ? 'font-semibold text-indigo-300' : 'hover:text-indigo-200'
            }
          >
            Recherche de Similarité
          </NavLink>
          <NavLink 
            to="/priorisation" 
            className={({ isActive }) => 
              isActive ? 'font-semibold text-indigo-300' : 'hover:text-indigo-200'
            }
          >
            Prédiction & Priorisation
          </NavLink>
        </div>
      </div>
    </nav>
  );
}

// Composant principal App avec navigation et routes
export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* En-tête de l'application */}
      <Header />
      {/* Contenu principal avec les routes */}
      <main className="flex-grow container mx-auto p-4">
        <Routes>
          <Route path="/" element={<SimilaritySearch />} />
          <Route path="/priorisation" element={<PriorityPrediction />} />
        </Routes>
      </main>
    </div>
  );
}
