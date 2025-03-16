import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

interface Result {
  id: number;
  title: string;
  pertinence: number;
  content: string;
}

const SearchAdvanced: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [searchType, setSearchType] = useState<string>('Recherche avancée');
  const [searchMode, setSearchMode] = useState<'index' | 'content'>('index');
  const [results, setResults] = useState<Result[]>([]);
  const [suggestions, setSuggestions] = useState<Result[]>([]);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const q = params.get('query') || '';
    setQuery(q);
    if (q) handleSearch(q);
  }, [location.search]);

  const handleSearch = (searchQuery: string) => {
    try {
      const regex = new RegExp(searchQuery, 'i');
      const mockResults = [
        { id: 1, title: 'Livre 1', pertinence: 95, content: 'Un extrait de contenu...' },
        { id: 2, title: 'Livre 2', pertinence: 87, content: 'Another excerpt...' },
        { id: 3, title: 'Livre 3', pertinence: 78, content: 'Un exemple de contenu pertinent...' },
        { id: 4, title: 'Livre 4', pertinence: 65, content: 'Another pertinent excerpt...' },
        { id: 5, title: 'Livre 5', pertinence: 92, content: 'Un exemple de contenu trouvé...' },
        { id: 6, title: 'Livre 6', pertinence: 83, content: 'Another found excerpt...' },
        { id: 7, title: 'Livre 7', pertinence: 70, content: 'Mot-clé trouvé dans ce contexte...' },
        { id: 8, title: 'Livre 8', pertinence: 88, content: 'Keyword in another context...' },
        { id: 9, title: 'Livre 9', pertinence: 60, content: 'Dernier exemple de résultat...' },
        { id: 10, title: 'Livre 10', pertinence: 75, content: 'Last result excerpt...' },
        { id: 11, title: 'Livre 11', pertinence: 91, content: 'Dernier exemple pertinent...' },
        { id: 12, title: 'Livre 12', pertinence: 82, content: 'Last pertinent result...' },
        { id: 13, title: 'Livre 13', pertinence: 67, content: 'Dernier résultat dans ce contexte...' },
      ].filter((r) => (searchMode === 'index' ? regex.test(r.title) : regex.test(r.content)));

      const sortedResults = mockResults.sort((a, b) => b.pertinence - a.pertinence);
      setResults(sortedResults);

      const topIds = sortedResults.slice(0, 2).map((r) => r.id);
      const mockSuggestions = [
        { id: 14, title: 'Livre 14', pertinence: 55, content: 'Suggestion liée...' },
        { id: 15, title: 'Livre 15', pertinence: 62, content: 'Autre suggestion...' },
      ].filter((s) => !topIds.includes(s.id));
      setSuggestions(mockSuggestions);
    } catch (error) {
      console.error('Invalid RegEx:', error);
      setResults([]);
      setSuggestions([]);
    }
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
          Recherche Avancée
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
                  placeholder="Entrez une expression RegEx"
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
              <div className="flex justify-center space-x-8">
                <label className="flex items-center space-x-2 text-teal-700 font-medium">
                  <input
                    type="radio"
                    value="index"
                    checked={searchMode === 'index'}
                    onChange={() => setSearchMode('index')}
                    className="text-teal-600 focus:ring-teal-500"
                  />
                  <span>Index</span>
                </label>
                <label className="flex items-center space-x-2 text-teal-700 font-medium">
                  <input
                    type="radio"
                    value="content"
                    checked={searchMode === 'content'}
                    onChange={() => setSearchMode('content')}
                    className="text-teal-600 focus:ring-teal-500"
                  />
                  <span>Contenu</span>
                </label>
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
        {results.length > 0 ? (
          <>
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
            {suggestions.length > 0 && (
              <div className="mt-12 max-w-5xl mx-auto">
                <h2 className="text-2xl font-semibold text-teal-700 mb-4">
                  Suggestions similaires
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
                          <span className="text-sm text-teal-500">
                            Pertinence: {suggestion.pertinence}%
                          </span>
                        </div>
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
            )}
          </>
        ) : (
          <p className="text-center text-gray-700">Aucun résultat trouvé pour "{query}". Essayez une autre recherche.</p>
        )}
      </main>
    </div>
  );
};

export default SearchAdvanced;