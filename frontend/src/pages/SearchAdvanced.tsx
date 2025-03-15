import { useState } from 'react';

interface Result {
  id: number;
  title: string;
  pertinence: number;
}

const SearchAdvanced: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [searchType, setSearchType] = useState<'index' | 'content'>('index');
  const [results, setResults] = useState<Result[]>([]);

  const handleSearch = () => {
    setResults([
      { id: 1, title: 'Livre 1', pertinence: 15 },
      { id: 2, title: 'Livre 2', pertinence: 10 },
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
              placeholder="Entrez une expression RegEx"
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
        <div className="mt-6 flex justify-center space-x-8">
          <label className="flex items-center space-x-2 text-gray-700 font-medium">
            <input
              type="radio"
              value="index"
              checked={searchType === 'index'}
              onChange={() => setSearchType('index')}
              className="text-indigo-600 focus:ring-indigo-500"
            />
            <span>Index</span>
          </label>
          <label className="flex items-center space-x-2 text-gray-700 font-medium">
            <input
              type="radio"
              value="content"
              checked={searchType === 'content'}
              onChange={() => setSearchType('content')}
              className="text-indigo-600 focus:ring-indigo-500"
            />
            <span>Contenu</span>
          </label>
        </div>
        {results.length > 0 && (
          <ul className="mt-10 max-w-3xl mx-auto space-y-4">
            {results.map((result) => (
              <li
                key={result.id}
                className="p-4 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200"
              >
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-gray-800">
                    {result.title}
                  </h3>
                  <span className="text-sm text-gray-500">
                    Pertinence: {result.pertinence}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </main>
      <footer className="text-center py-6">
        <a
          href="/"
          className="text-indigo-600 hover:text-indigo-800 font-medium transition-colors duration-200"
        >
          Retour à la recherche simple
        </a>
      </footer>
    </div>
  );
};

export default SearchAdvanced;