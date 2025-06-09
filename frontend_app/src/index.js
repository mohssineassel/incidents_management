import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';  // Importation des styles TailwindCSS

// Sélection de l'élément HTML racine
const container = document.getElementById('root');
const root = createRoot(container);

// Rendu de l'application React englobée par le router
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
