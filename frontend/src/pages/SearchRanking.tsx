import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

interface Result {
  id: number;
  title: string;
  language: string;
  excerpt: string;
  occurrences: number;
  centralityScore?: number;
}

const SearchRanking: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [rankingType, setRankingType] = useState<string>('occurrences');
  const [results, setResults] = useState<Result[]>([]);
  const [searchType, setSearchType] = useState<string>('Classement');
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const q = params.get('query') || '';
    setQuery(q);
    if (q) handleSearch(q);
  }, [location.search]);

  const handleSearch = (searchQuery: string) => {
    const mockResults = [
      { id: 1, title: 'Livre 1', language: 'fr', excerpt: 'Un extrait de contenu...', occurrences: 5, centralityScore: 0.85 },
      { id: 2, title: 'Livre 2', language: 'en', excerpt: 'Un autre extrait de contenu...', occurrences: 3, centralityScore: 0.72 },
      { id: 3, title: 'Livre 3', language: 'fr', excerpt: 'Un exemple de contenu pertinent...', occurrences: 8, centralityScore: 0.91 },
      { id: 4, title: 'Livre 4', language: 'en', excerpt: 'Un autre exemple de contenu pertinent...', occurrences: 2, centralityScore: 0.65 },
      { id: 5, title: 'Livre 5', language: 'fr', excerpt: 'Un exemple de contenu trouvé...', occurrences: 6, centralityScore: 0.78 },
      { id: 6, title: 'Livre 6', language: 'en', excerpt: 'Un autre exemple de contenu trouvé...', occurrences: 4, centralityScore: 0.70 },
      { id: 7, title: 'Livre 7', language: 'fr', excerpt: 'Mot-clé trouvé dans ce contexte...', occurrences: 7, centralityScore: 0.88 },
      { id: 8, title: 'Livre 8', language: 'en', excerpt: 'Mot-clé trouvé dans un autre contexte...', occurrences: 1, centralityScore: 0.60 },
      { id: 9, title: 'Livre 9', language: 'fr', excerpt: 'Dernier exemple de résultat...', occurrences: 9, centralityScore: 0.95 },
      { id: 10, title: 'Livre 10', language: 'en', excerpt: 'Dernier exemple de résultat trouvé...', occurrences: 3, centralityScore: 0.73 },
    ].filter((r) =>
      r.excerpt.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.title.toLowerCase().includes(searchQuery.toLowerCase())
    );

    let sortedResults: Result[];
    if (rankingType === 'centrality') {
      sortedResults = [...mockResults].sort((a, b) => (b.centralityScore || 0) - (a.centralityScore || 0));
    } else {
      sortedResults = [...mockResults].sort((a, b) => b.occurrences - a.occurrences);
    }
    setResults(sortedResults);
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
          Classement des Résultats
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
              <div className="flex justify-center space-x-8">
                <label className="flex items-center space-x-2 text-teal-700 font-medium">
                  <input
                    type="radio"
                    value="occurrences"
                    checked={rankingType === 'occurrences'}
                    onChange={() => setRankingType('occurrences')}
                    className="text-teal-600 focus:ring-teal-500"
                  />
                  <span>Occurrences</span>
                </label>
                <label className="flex items-center space-x-2 text-teal-700 font-medium">
                  <input
                    type="radio"
                    value="centrality"
                    checked={rankingType === 'centrality'}
                    onChange={() => setRankingType('centrality')}
                    className="text-teal-600 focus:ring-teal-500"
                  />
                  <span>Centralité</span>
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
                  <div className="text-right text-sm text-gray-600">
                    {rankingType === 'centrality'
                      ? `Centralité: ${(result.centralityScore || 0).toFixed(2)}`
                      : `Occurrences: ${result.occurrences}`}
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
        ) : (
          <p className="text-center text-gray-700">Aucun résultat trouvé pour "{query}". Essayez une autre recherche.</p>
        )}
      </main>
    </div>
  );
};

export default SearchRanking;