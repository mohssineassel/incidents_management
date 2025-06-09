import React, { useState, useEffect, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, LineChart, Line, PieChart, Pie, Cell, Heatmap } from 'recharts';
import { Search, Zap, Target, TrendingUp, Eye, Filter, Download, RefreshCw } from 'lucide-react';

const SimilarityDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedMethod, setSelectedMethod] = useState('hybrid');
  const [searchQuery, setSearchQuery] = useState('');
  const [similarityResults, setSimilarityResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Données simulées pour la démonstration
  const mockIncidents = [
    { id: 1, description: "Serveur Apache ne répond plus, erreur 500", category: "Web Server", priority: "Critical", similarity: 0.95 },
    { id: 2, description: "Base de données MySQL inaccessible", category: "Database", priority: "High", similarity: 0.87 },
    { id: 3, description: "Application web lente, temps de réponse élevé", category: "Application", priority: "Medium", similarity: 0.73 },
    { id: 4, description: "Erreur certificat SSL domaine principal", category: "Security", priority: "High", similarity: 0.68 },
    { id: 5, description: "Service Exchange en panne", category: "Infrastructure", priority: "Critical", similarity: 0.45 }
  ];

  const methodsComparison = [
    { method: 'TF-IDF', accuracy: 0.78, speed: 0.95, memory: 0.85, overall: 0.86 },
    { method: 'SBERT', accuracy: 0.92, speed: 0.70, memory: 0.60, overall: 0.74 },
    { method: 'Hybrid', accuracy: 0.94, speed: 0.82, memory: 0.72, overall: 0.83 }
  ];

  const clusterData = [
    { cluster: 'Database Issues', count: 25, avgSimilarity: 0.84, color: '#8884d8' },
    { cluster: 'Web Server Errors', count: 18, avgSimilarity: 0.79, color: '#82ca9d' },
    { cluster: 'Network Problems', count: 15, avgSimilarity: 0.72, color: '#ffc658' },
    { cluster: 'Security Alerts', count: 12, avgSimilarity: 0.88, color: '#ff7300' },
    { cluster: 'Application Crashes', count: 20, avgSimilarity: 0.76, color: '#8dd1e1' }
  ];

  const similarityDistribution = [
    { range: '0.0-0.2', count: 45, percentage: 15 },
    { range: '0.2-0.4', count: 67, percentage: 22 },
    { range: '0.4-0.6', count: 89, percentage: 30 },
    { range: '0.6-0.8', count: 72, percentage: 24 },
    { range: '0.8-1.0', count: 27, percentage: 9 }
  ];

  const performanceMetrics = [
    { metric: 'Précision Moyenne', value: 0.847, trend: '+12%', color: 'text-green-600' },
    { metric: 'Temps de Réponse', value: '142ms', trend: '-8%', color: 'text-blue-600' },
    { metric: 'Couverture', value: '94.2%', trend: '+5%', color: 'text-purple-600' },
    { metric: 'F1-Score', value: '0.891', trend: '+15%', color: 'text-orange-600' }
  ];

  const handleSearch = () => {
    setIsLoading(true);
    // Simulation d'une recherche
    setTimeout(() => {
      setSimilarityResults(mockIncidents.filter(incident => 
        incident.description.toLowerCase().includes(searchQuery.toLowerCase())
      ));
      setIsLoading(false);
    }, 1000);
  };

  const SimilarityHeatmap = () => {
    const heatmapData = Array.from({ length: 10 }, (_, i) =>
      Array.from({ length: 10 }, (_, j) => ({
        x: i,
        y: j,
        value: Math.random() * 0.8 + 0.2
      }))
    ).flat();

    return (
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h3 className="text-xl font-bold mb-4 flex items-center">
          <Eye className="mr-2 text-blue-600" size={20} />
          Matrice de Similarité Interactive
        </h3>
        <div className="grid grid-cols-10 gap-1">
          {heatmapData.map((cell, idx) => (
            <div
              key={idx}
              className="w-8 h-8 rounded cursor-pointer transition-all hover:scale-110"
              style={{
                backgroundColor: `rgba(59, 130, 246, ${cell.value})`,
              }}
              title={`Similarité: ${cell.value.toFixed(3)}`}
            />
          ))}
        </div>
        <div className="mt-4 flex justify-between text-sm text-gray-600">
          <span>Faible similarité</span>
          <span>Forte similarité</span>
        </div>
      </div>
    );
  };

  const NetworkGraph = () => {
    const nodes = Array.from({ length: 8 }, (_, i) => ({
      id: i,
      x: 200 + 150 * Math.cos((i * 2 * Math.PI) / 8),
      y: 200 + 150 * Math.sin((i * 2 * Math.PI) / 8),
      size: 10 + Math.random() * 15,
      similarity: Math.random()
    }));

    return (
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h3 className="text-xl font-bold mb-4 flex items-center">
          <Target className="mr-2 text-green-600" size={20} />
          Réseau de Similarité
        </h3>
        <svg width="400" height="400" className="border rounded">
          {/* Connexions */}
          {nodes.map((node1, i) =>
            nodes.slice(i + 1).map((node2, j) => {
              const distance = Math.sqrt(
                Math.pow(node1.x - node2.x, 2) + Math.pow(node1.y - node2.y, 2)
              );
              if (distance < 200) {
                return (
                  <line
                    key={`${i}-${j}`}
                    x1={node1.x}
                    y1={node1.y}
                    x2={node2.x}
                    y2={node2.y}
                    stroke="#e5e7eb"
                    strokeWidth={Math.max(1, 3 - distance / 100)}
                    opacity={0.6}
                  />
                );
              }
              return null;
            })
          )}
          {/* Nœuds */}
          {nodes.map((node, i) => (
            <circle
              key={i}
              cx={node.x}
              cy={node.y}
              r={node.size}
              fill={`hsl(${node.similarity * 120}, 70%, 50%)`}
              className="cursor-pointer hover:opacity-80 transition-opacity"
              title={`Incident ${i + 1}`}
            />
          ))}
        </svg>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <Zap className="mr-3 text-blue-600" size={32} />
                Système de Similarité Avancé
              </h1>
              <p className="text-gray-600 mt-2">
                Analyse intelligente des incidents IT avec IA multi-modèles
              </p>
            </div>
            <div className="flex space-x-2">
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center">
                <Download size={16} className="mr-2" />
                Exporter
              </button>
              <button className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors flex items-center">
                <RefreshCw size={16} className="mr-2" />
                Actualiser
              </button>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow-lg mb-6">
          <div className="flex border-b">
            {[
              { id: 'overview', label: 'Vue d\'ensemble', icon: TrendingUp },
              { id: 'search', label: 'Recherche', icon: Search },
              { id: 'analysis', label: 'Analyse', icon: Eye },
              { id: 'comparison', label: 'Comparaison', icon: Filter }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center px-6 py-4 font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <tab.icon size={18} className="mr-2" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Métriques de performance */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {performanceMetrics.map((metric, idx) => (
                <div key={idx} className="bg-white p-6 rounded-lg shadow-lg">
                  <h3 className="text-sm font-medium text-gray-600">{metric.metric}</h3>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-2xl font-bold text-gray-900">{metric.value}</span>
                    <span className={`text-sm font-medium ${metric.color}`}>
                      {metric.trend}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Graphiques principaux */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Distribution des similarités */}
              <div className="bg-white p-6 rounded-lg shadow-lg">
                <h3 className="text-xl font-bold mb-4">Distribution des Similarités</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={similarityDistribution}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="range" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Clustering */}
              <div className="bg-white p-6 rounded-lg shadow-lg">
                <h3 className="text-xl font-bold mb-4">Clusters d'Incidents</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={clusterData}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="count"
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {clusterData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Visualisations avancées */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SimilarityHeatmap />
              <NetworkGraph />
            </div>
          </div>
        )}

        {activeTab === 'search' && (
          <div className="space-y-6">
            {/* Interface de recherche */}
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-bold mb-4 flex items-center">
                <Search className="mr-2 text-blue-600" size={20} />
                Recherche de Similarité
              </h3>
              <div className="flex space-x-4 mb-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Décrivez votre incident..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <select
                  value={selectedMethod}
                  onChange={(e) => setSelectedMethod(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="tfidf">TF-IDF</option>
                  <option value="sbert">SBERT</option>
                  <option value="hybrid">Hybride</option>
                </select>
                <button
                  onClick={handleSearch}
                  disabled={isLoading}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {isLoading ? 'Recherche...' : 'Rechercher'}
                </button>
              </div>

              {/* Résultats de recherche */}
              {similarityResults.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-semibold text-gray-900">Incidents similaires trouvés:</h4>
                  {similarityResults.map((incident, idx) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{incident.description}</p>
                          <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                              {incident.category}
                            </span>
                            <span className={`px-2 py-1 rounded ${
                              incident.priority === 'Critical' ? 'bg-red-100 text-red-800' :
                              incident.priority === 'High' ? 'bg-orange-100 text-orange-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {incident.priority}
                            </span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-blue-600">
                            {(incident.similarity * 100).toFixed(1)}%
                          </div>
                          <div className="text-sm text-gray-600">Similarité</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="space-y-6">
            {/* Analyse comparative */}
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-bold mb-4">Analyse de Performance par Méthode</h3>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={methodsComparison}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="method" />
                  <YAxis domain={[0, 1]} />
                  <Tooltip formatter={(value) => `${(value * 100).toFixed(1)}%`} />
                  <Legend />
                  <Line type="monotone" dataKey="accuracy" stroke="#8884d8" strokeWidth={3} name="Précision" />
                  <Line type="monotone" dataKey="speed" stroke="#82ca9d" strokeWidth={3} name="Rapidité" />
                  <Line type="monotone" dataKey="memory" stroke="#ffc658" strokeWidth={3} name="Efficacité Mémoire" />
                  <Line type="monotone" dataKey="overall" stroke="#ff7300" strokeWidth={3} name="Score Global" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Matrice de confusion simulée */}
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-bold mb-4">Matrice de Confusion - Validation</h3>
              <div className="grid grid-cols-3 gap-2 max-w-md">
                {[
                  [85, 12, 3],
                  [8, 78, 14],
                  [5, 15, 80]
                ].map((row, i) => 
                  row.map((cell, j) => (
                    <div 
                      key={`${i}-${j}`}
                      className={`p-4 text-center font-bold rounded ${
                        i === j ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {cell}
                    </div>
                  ))
                )}
              </div>
              <div className="mt-4 text-sm text-gray-600">
                <p>Précision globale: 89.3%</p>
                <p>F1-Score moyen: 0.891</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'comparison' && (
          <div className="space-y-6">
            {/* Comparaison détaillée des méthodes */}
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-bold mb-4">Comparaison Détaillée des Algorithmes</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b">
                      <th className="pb-3 font-semibold">Critère</th>
                      <th className="pb-3 font-semibold text-center">TF-IDF</th>
                      <th className="pb-3 font-semibold text-center">SBERT</th>
                      <th className="pb-3 font-semibold text-center">Hybride</th>
                    </tr>
                  </thead>
                  <tbody className="space-y-2">
                    {[
                      { metric: 'Précision', tfidf: '78%', sbert: '92%', hybrid: '94%' },
                      { metric: 'Rappel', tfidf: '82%', sbert: '89%', hybrid: '91%' },
                      { metric: 'Temps de traitement', tfidf: '50ms', sbert: '280ms', hybrid: '165ms' },
                      { metric: 'Mémoire utilisée', tfidf: '120MB', sbert: '380MB', hybrid: '250MB' },
                      { metric: 'Scalabilité', tfidf: 'Excellente', sbert: 'Bonne', hybrid: 'Très bonne' }
                    ].map((row, idx) => (
                      <tr key={idx} className="border-b border-gray-100">
                        <td className="py-3 font-medium">{row.metric}</td>
                        <td className="py-3 text-center">{row.tfidf}</td>
                        <td className="py-3 text-center">{row.sbert}</td>
                        <td className="py-3 text-center font-semibold text-blue-600">{row.hybrid}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Recommandations */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
              <h3 className="text-xl font-bold mb-4 text-blue-900">💡 Recommandations</h3>
              <div className="space-y-3 text-blue-800">
                <p><strong>Pour la production:</strong> Utilisez l'approche hybride pour optimiser précision et performance</p>
                <p><strong>Pour le développement:</strong> TF-IDF pour les tests rapides, SBERT pour l'analyse approfondie</p>
                <p><strong>Mise à l'échelle:</strong> Implémentez FAISS pour gérer des volumes importants (100k incidents)</p>
                <p><strong>Optimisation:</strong> Réentraînement mensuel des modèles avec les nouveaux incidents</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SimilarityDashboard;