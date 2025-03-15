import { useState } from 'react';

interface Result {
  id: number;
  title: string;
}

const Dashboard: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<Result[]>([]);

  const history = ['mot1', 'mot2', 'mot3'];
  const favorites = ['Livre Favori 1', 'Livre Favori 2'];

  const handleSearch = () => {
    setResults([{ id: 1, title: 'Résultat 1' }, { id: 2, title: 'Résultat 2' }]);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-1/4 bg-white p-6 shadow-lg">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Menu</h2>
        <ul className="space-y-6">
          <li>
            <a
              href="#"
              className="text-indigo-600 hover:text-indigo-800 font-semibold transition-colors duration-200"
            >
              Recherche
            </a>
          </li>
          <li>
            <h3 className="text-lg font-semibold text-gray-700 mb-2">
              Historique
            </h3>
            <ul className="space-y-2">
              {history.map((item, idx) => (
                <li
                  key={idx}
                  className="text-sm text-gray-600 hover:text-indigo-600 transition-colors duration-200"
                >
                  {item}
                </li>
              ))}
            </ul>
          </li>
          <li>
            <h3 className="text-lg font-semibold text-gray-700 mb-2">
              Favoris
            </h3>
            <ul className="space-y-2">
              {favorites.map((item, idx) => (
                <li
                  key={idx}
                  className="text-sm text-gray-600 flex items-center space-x-1"
                >
                  <span className="text-yellow-500">⭐</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </li>
        </ul>
      </aside>
      <div className="flex-1">
        <header className="bg-white shadow-md py-6">
          <div className="flex justify-center">
            <div className="w-full max-w-3xl flex items-center space-x-4">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Entrez un mot-clé"
                className="flex-1 p-4 text-lg border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
              />
              <button
                onClick={handleSearch}
                className="px-6 py-4 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 transition-colors duration-200"
              >
                Rechercher
              </button>
            </div>
          </div>
        </header>
        <main className="container mx-auto px-4 py-10">
          {results.length === 0 ? (
            <p className="text-center text-gray-500 text-lg">
              Effectuez une recherche pour voir les résultats
            </p>
          ) : (
            <ul className="max-w-3xl mx-auto space-y-4">
              {results.map((result) => (
                <li
                  key={result.id}
                  className="p-4 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200"
                >
                  <h3 className="text-lg font-semibold text-gray-800">
                    {result.title}
                  </h3>
                </li>
              ))}
            </ul>
          )}
        </main>
      </div>
    </div>
  );
};

export default Dashboard;