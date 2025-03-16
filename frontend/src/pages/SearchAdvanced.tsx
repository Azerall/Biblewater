import { useState } from 'react';
import { Link } from 'react-router-dom';

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
      { id: 1, title: 'Livre 1', pertinence: 95 },
      { id: 2, title: 'Livre 2', pertinence: 87 },
      { id: 3, title: 'Livre 3', pertinence: 78 },
      { id: 4, title: 'Livre 4', pertinence: 65 },
      { id: 5, title: 'Livre 5', pertinence: 92 },
      { id: 6, title: 'Livre 6', pertinence: 83 },
      { id: 7, title: 'Livre 7', pertinence: 70 },
      { id: 8, title: 'Livre 8', pertinence: 88 },
      { id: 9, title: 'Livre 9', pertinence: 60 },
      { id: 10, title: 'Livre 10', pertinence: 75 },
      { id: 11, title: 'Livre 11', pertinence: 91 },
      { id: 12, title: 'Livre 12', pertinence: 82 },
      { id: 13, title: 'Livre 13', pertinence: 67 },
    ]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-t from-teal-50 to-yellow-50">
      <header className="py-10 text-center">
        <h1 className="text-4xl font-extrabold text-teal-600 animate-bounce">
          Biblewater
        </h1>
      </header>
      <main className="container mx-auto px-6 py-12">
        <div className="flex justify-center">
          <div className="w-full max-w-lg flex items-center space-x-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Entrez une expression RegEx"
              className="flex-1 p-4 text-lg bg-white border-2 border-teal-300 rounded-xl shadow-md focus:outline-none focus:border-teal-500 transition-all duration-300"
            />
            <button
              onClick={handleSearch}
              className="px-8 py-4 bg-yellow-400 text-teal-900 font-bold rounded-xl shadow-md hover:bg-yellow-300 hover:rotate-2 transition-all duration-300"
            >
              C’est parti !
            </button>
          </div>
        </div>
        <div className="mt-6 flex justify-center space-x-8">
          <label className="flex items-center space-x-2 text-teal-700 font-medium">
            <input
              type="radio"
              value="index"
              checked={searchType === 'index'}
              onChange={() => setSearchType('index')}
              className="text-teal-600 focus:ring-teal-500"
            />
            <span>Index</span>
          </label>
          <label className="flex items-center space-x-2 text-teal-700 font-medium">
            <input
              type="radio"
              value="content"
              checked={searchType === 'content'}
              onChange={() => setSearchType('content')}
              className="text-teal-600 focus:ring-teal-500"
            />
            <span>Contenu</span>
          </label>
        </div>
        {results.length > 0 && (
          <ul className="mt-12 max-w-5xl mx-auto grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            {results.map((result) => (
              <li
                key={result.id}
                className="p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
              >
                <div className="flex flex-col space-y-2">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-teal-700">
                      {result.title}
                    </h3>
                    <span className="text-sm text-teal-500">
                      Pertinence: {result.pertinence}%
                    </span>
                  </div>
                  <Link
                    to={`/book/${result.id}`}
                    className="text-yellow-500 hover:text-yellow-600 font-medium text-right"
                  >
                    Lire
                  </Link>
                </div>
              </li>
            ))}
          </ul>
        )}
      </main>
      <footer className="text-center py-8">
        <a
          href="/"
          className="text-teal-600 hover:text-teal-800 font-semibold transition-colors duration-300"
        >
          Retour à la recherche simple
        </a>
      </footer>
    </div>
  );
};

export default SearchAdvanced;