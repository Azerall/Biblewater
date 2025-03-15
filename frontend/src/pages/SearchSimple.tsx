import { useState } from 'react';

interface Result {
  id: number;
  title: string;
  excerpt: string;
}

const SearchSimple: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<Result[]>([]);

  const handleSearch = () => {
    setResults([
      { id: 1, title: 'Livre 1', excerpt: 'Mot-clé trouvé ici...' },
      { id: 2, title: 'Livre 2', excerpt: 'Un autre extrait...' },
    ]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <header className="bg-white shadow-md py-6">
        <h1 className="text-3xl font-extrabold text-center text-gray-800 tracking-tight">
          Moteur de Recherche
        </h1>
      </header>
      <main className="container mx-auto px-4 py-10">
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
        {results.length > 0 && (
          <ul className="mt-10 max-w-3xl mx-auto space-y-4">
            {results.map((result) => (
              <li
                key={result.id}
                className="p-4 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800">
                      {result.title}
                    </h3>
                    <p className="text-sm text-gray-600">{result.excerpt}</p>
                  </div>
                  <button className="text-indigo-600 hover:text-indigo-800 font-medium">
                    Voir plus
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </main>
      <footer className="text-center py-6">
        <a
          href="/advanced"
          className="text-indigo-600 hover:text-indigo-800 font-medium transition-colors duration-200"
        >
          Recherche avancée
        </a>
      </footer>
    </div>
  );
};

export default SearchSimple;