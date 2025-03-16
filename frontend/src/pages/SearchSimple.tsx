import { useState } from 'react';
import { Link } from 'react-router-dom';

interface Result {
  id: number;
  title: string;
  language: string;
  excerpt: string;
}

const SearchSimple: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<Result[]>([]);

  const handleSearch = () => {
    setResults([
      { id: 1, title: 'Livre 1', language: 'fr', excerpt: 'Un extrait de contenu...' },
      { id: 2, title: 'Livre 2', language: 'en', excerpt: 'Un autre extrait de contenu...' },
      { id: 3, title: 'Livre 3', language: 'fr', excerpt: 'Un exemple de contenu pertinent...' },
      { id: 4, title: 'Livre 4', language: 'en', excerpt: 'Un autre exemple de contenu pertinent...' },
      { id: 5, title: 'Livre 5', language: 'fr', excerpt: 'Un exemple de contenu trouvé...' },
      { id: 6, title: 'Livre 6', language: 'en', excerpt: 'Un autre exemple de contenu trouvé...' },
      { id: 7, title: 'Livre 7', language: 'fr', excerpt: 'Mot-clé trouvé dans ce contexte...' },
      { id: 8, title: 'Livre 8', language: 'en', excerpt: 'Mot-clé trouvé dans un autre contexte...' },
      { id: 9, title: 'Livre 9', language: 'fr', excerpt: 'Dernier exemple de résultat...' },
      { id: 10, title: 'Livre 10', language: 'en', excerpt: 'Dernier exemple de résultat trouvé...' },
      { id: 11, title: 'Livre 11', language: 'fr', excerpt: 'Dernier exemple de résultat pertinent...' },
      { id: 12, title: 'Livre 12', language: 'en', excerpt: 'Dernier exemple de résultat pertinent trouvé...' },
      { id: 13, title: 'Livre 13', language: 'fr', excerpt: 'Dernier exemple de résultat trouvé dans ce contexte...' },
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
              placeholder="Trouve ton livre..."
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
                    <span className="text-sm text-teal-500">({result.language})</span>
                  </div>
                  <p className="text-sm text-gray-500">
                    {result.excerpt.length > 20
                      ? `${result.excerpt.slice(0, 20)}...`
                      : result.excerpt}
                  </p>
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
          href="/advanced"
          className="text-teal-600 hover:text-teal-800 font-semibold transition-colors duration-300"
        >
          Recherche avancée
        </a>
      </footer>
    </div>
  );
};

export default SearchSimple;