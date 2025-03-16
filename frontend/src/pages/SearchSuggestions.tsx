import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

interface Result {
  id: number;
  title: string;
  language: string;
  excerpt: string;
  occurrences: number;
}

const SearchSuggestions: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [searchType, setSearchType] = useState<string>('Suggestions');
  const [suggestions, setSuggestions] = useState<Result[]>([]);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const q = params.get('query') || '';
    setQuery(q);
    if (q) generateSuggestions(q);
  }, [location.search]);

  const generateSuggestions = (searchQuery: string) => {
    const mockResults = [
      { id: 1, title: 'Livre 1', language: 'fr', excerpt: 'Un extrait de contenu...', occurrences: 5 },
      { id: 2, title: 'Livre 2', language: 'en', excerpt: 'Un autre extrait de contenu...', occurrences: 3 },
      { id: 3, title: 'Livre 3', language: 'fr', excerpt: 'Un exemple de contenu pertinent...', occurrences: 8 },
      { id: 4, title: 'Livre 4', language: 'en', excerpt: 'Un autre exemple de contenu pertinent...', occurrences: 2 },
      { id: 5, title: 'Livre 5', language: 'fr', excerpt: 'Un exemple de contenu trouvé...', occurrences: 6 },
      { id: 6, title: 'Livre 6', language: 'en', excerpt: 'Un autre exemple de contenu trouvé...', occurrences: 4 },
      { id: 7, title: 'Livre 7', language: 'fr', excerpt: 'Mot-clé trouvé dans ce contexte...', occurrences: 7 },
      { id: 8, title: 'Livre 8', language: 'en', excerpt: 'Mot-clé trouvé dans un autre contexte...', occurrences: 1 },
      { id: 9, title: 'Livre 9', language: 'fr', excerpt: 'Dernier exemple de résultat...', occurrences: 9 },
      { id: 10, title: 'Livre 10', language: 'en', excerpt: 'Dernier exemple de résultat trouvé...', occurrences: 3 },
    ].filter((r) =>
      r.excerpt.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.title.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const sortedResults = mockResults.sort((a, b) => b.occurrences - a.occurrences);
    const topIds = sortedResults.slice(0, 2).map((r) => r.id);

    const mockSuggestions = [
      { id: 11, title: 'Livre 11', language: 'fr', excerpt: 'Suggestion liée...', occurrences: 2 },
      { id: 12, title: 'Livre 12', language: 'en', excerpt: 'Autre suggestion...', occurrences: 1 },
      { id: 13, title: 'Livre 13', language: 'fr', excerpt: 'Suggestion pertinente...', occurrences: 4 },
    ].filter((s) => !topIds.includes(s.id));

    setSuggestions(mockSuggestions);
  };

  const handleNewSearch = () => {
    if (query.trim()) {
      const path = searchType === 'Recherche' ? `/search?query=${encodeURIComponent(query)}` :
                     searchType === 'Recherche avancée' ? `/advanced?query=${encodeURIComponent(query)}` :
                     searchType === 'Classement' ? `/ranking?query=${encodeURIComponent(query)}` :
                     searchType === 'Suggestions' ? `/suggestions?query=${encodeURIComponent(query)}` :
                     '/';
      navigate(path);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-t from-teal-50 to-yellow-50">
      <header className="py-10 text-center">
        <h1 className="text-4xl font-extrabold text-teal-600 animate-bounce">
          Suggestions de Recherche
        </h1>
      </header>
      <div className="sticky top-0 z-10 bg-gradient-to-t from-teal-50 to-yellow-50 py-4">
        <div className="container mx-auto px-6">
          <div className="flex justify-center">
            <div className="w-full max-w-lg space-y-4">
              <div className="relative">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Entrez votre recherche..."
                  className="w-full p-4 text-lg bg-white border-2 border-teal-300 rounded-xl shadow-md focus:outline-none focus:border-teal-500 transition-all duration-300"
                />
                <select
                  value={searchType}
                  onChange={(e) => setSearchType(e.target.value)}
                  className="absolute right-2 top-2 p-2 bg-teal-300 text-white rounded-md shadow-md focus:outline-none hover:bg-teal-400 transition-all duration-300"
                >
                  <option value="Recherche">Recherche</option>
                  <option value="Recherche avancée">Recherche avancée</option>
                  <option value="Classement">Classement</option>
                  <option value="Suggestions">Suggestions</option>
                </select>
              </div>
              <button
                onClick={handleNewSearch}
                className="w-full px-8 py-4 bg-teal-600 text-white font-bold rounded-xl shadow-md hover:bg-teal-700 hover:rotate-2 transition-all duration-300"
              >
                Rechercher
              </button>
              <div className="text-center">
                <Link
                  to="/"
                  className="text-teal-600 hover:text-teal-800 font-semibold transition-colors duration-300"
                >
                  Retour à l’accueil
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
      <main className="container mx-auto px-6 py-12">
        {suggestions.length > 0 ? (
          <div className="mt-12 max-w-5xl mx-auto">
            <h2 className="text-2xl font-semibold text-teal-700 mb-4">
              Suggestions similaires pour "{query}"
            </h2>
            <ul className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
              {suggestions.map((suggestion) => (
                <li
                  key={suggestion.id}
                  className="p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  <div className="flex flex-col space-y-2">
                    <div className="flex justify-between items-center">
                      <h3 className="text-lg font-semibold text-teal-700">
                        {suggestion.title}
                      </h3>
                      <span className="text-sm text-teal-500">({suggestion.language})</span>
                    </div>
                    <p className="text-sm text-gray-500">
                      {suggestion.excerpt.length > 20
                        ? `${suggestion.excerpt.slice(0, 20)}...`
                        : suggestion.excerpt}
                    </p>
                    <Link
                      to={`/book/${suggestion.id}`}
                      className="text-yellow-500 hover:text-yellow-600 font-medium text-right"
                    >
                      Lire
                    </Link>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="text-center text-gray-700">
            Aucune suggestion trouvée pour "{query}". Essayez une autre recherche.
          </p>
        )}
      </main>
    </div>
  );
};

export default SearchSuggestions;