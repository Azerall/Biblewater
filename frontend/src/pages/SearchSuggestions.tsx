import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

interface Author {
  name: string;
}

interface Result {
  id: number;
  title: string;
  authors: Author[];
  language: string;
  score: number;
  occurrences: number;
}

interface Suggestion {
  id: number;
  title: string;
  authors: Author[];
  language: string;
}

interface SuggestionResponse {
  results: Result[];
  suggestions: Suggestion[];
}

const SearchSuggestions: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [word, setWord] = useState<string>(''); // Nouvel état pour le mot
  const [searchType, setSearchType] = useState<string>('Suggestions');
  const [rankingType, setRankingType] = useState<string>('occurrences'); // Nouvel état pour le critère de tri
  const [results, setResults] = useState<Result[]>([]); // Nouvel état pour les résultats
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1); // Page actuelle pour les résultats
  const [itemsPerPage] = useState<number>(9); // 9 livres par page pour les résultats
  const [firstTime, setFirstTime] = useState<boolean>(true); // Nouvel état pour la première fois
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const q = params.get('query') || '';
    setQuery(q);
    if (q && firstTime) {
      console.log("======= q =======", q);
      setFirstTime(false);
      fetchSuggestions(q);
    }
  }, [location.search]);

  const fetchSuggestions = async (searchQuery: string) => {
    setLoading(true);
    setError(null);
    try {
      if (!searchQuery.trim()) {
        throw new Error('La requête ne peut pas être vide.');
      }

      const response = await fetch(`http://127.0.0.1:8000/gutenberg/search_with_suggestions/${encodeURIComponent(searchQuery)}/`);
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status} - ${response.statusText}`);
      }
      const data: SuggestionResponse = await response.json();
      console.log("======= suggestions data =======", data);

      // Filtrer les résultats pour retirer les livres présents dans suggestions
      const suggestionIds = new Set(data.suggestions.map(suggestion => suggestion.id));
      const filteredResults = data.results.filter(result => !suggestionIds.has(result.id));

      setResults(filteredResults || []);
      setSuggestions(data.suggestions || []);
      setWord(searchQuery);
      setQuery(''); // Réinitialiser la requête pour éviter de recharger les suggestions
      setCurrentPage(1); // Réinitialiser la page à 1 après une nouvelle recherche
    } catch (err) {
      setError('Aucune suggestion trouvée ou une erreur est survenue. Veuillez réessayer.');
      console.error('Erreur détaillée:', err);
      setResults([]);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewSearch = async () => {
    if (query.trim()) {
      if (searchType === 'Suggestions') {
        await fetchSuggestions(query); // Exécute la recherche directement
      }
      const basePath =
        searchType === 'Recherche'
          ? `/search`
          : searchType === 'Recherche avancée'
          ? `/advanced`
          : searchType === 'Classement'
          ? `/ranking`
          : searchType === 'Suggestions'
          ? `/suggestions`
          : '/';

      const params = new URLSearchParams();
      params.append('query', encodeURIComponent(query));
      if (searchType === 'Classement') {
        params.append('ranking', encodeURIComponent(rankingType)); // Ajout du paramètre ranking pour Classement
      }

      const path = `${basePath}?${params.toString()}`;
      navigate(path);
    }
  };

  // Calculer les indices pour la pagination des résultats
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentResults = results.slice(indexOfFirstItem, indexOfLastItem);

  // Calculer le nombre total de pages pour les résultats
  const totalPages = Math.ceil(results.length / itemsPerPage);

  // Aller à la page précédente
  const handlePrevious = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  // Aller à la page suivante
  const handleNext = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  return (
    <div className="min-h-screen">
      <header className="py-10 text-center">
        <h1 className="text-4xl font-extrabold text-teal-600 animate-bounce">
          Suggestions de Recherche
        </h1>
      </header>
      <div className="sticky py-4">
        <div className="container mx-auto px-6">
          <div className="flex justify-center">
            <div className="w-full max-w-lg space-y-4">
              <div className="relative">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Entrez votre recherche..."
                  className="w-full p-4 text-lg bg-white border-2 border-teal-300 rounded-xl shadow-xl focus:outline-none focus:border-teal-500 transition-all duration-300"
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
              {searchType === 'Classement' && (
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
                      value="closeness"
                      checked={rankingType === 'closeness'}
                      onChange={() => setRankingType('closeness')}
                      className="text-teal-600 focus:ring-teal-500"
                    />
                    <span>Closeness</span>
                  </label>
                  <label className="flex items-center space-x-2 text-teal-700 font-medium">
                    <input
                      type="radio"
                      value="betweenness"
                      checked={rankingType === 'betweenness'}
                      onChange={() => setRankingType('betweenness')}
                      className="text-teal-600 focus:ring-teal-500"
                    />
                    <span>Betweenness</span>
                  </label>
                  <label className="flex items-center space-x-2 text-teal-700 font-medium">
                    <input
                      type="radio"
                      value="pagerank"
                      checked={rankingType === 'pagerank'}
                      onChange={() => setRankingType('pagerank')}
                      className="text-teal-600 focus:ring-teal-500"
                    />
                    <span>PageRank</span>
                  </label>
                </div>
              )}
              <button
                onClick={handleNewSearch}
                className="w-full px-8 py-4 bg-teal-600 text-white font-bold rounded-xl shadow-md hover:bg-teal-700 hover:rotate-2 transition-all duration-300"
                disabled={loading}
              >
                {loading ? 'Recherche en cours...' : 'Rechercher'}
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
        {error && (
          <p className="text-center text-red-600 mb-4">{error}</p>
        )}
        {loading ? (
          <p className="text-center text-gray-700">Chargement des suggestions...</p>
        ) : results.length > 0 || suggestions.length > 0 ? (
          <div className="mt-12 max-w-5xl mx-auto">
            {/* Section pour les résultats */}
            {results.length > 0 && (
              <>
                <h2 className="text-2xl font-semibold text-teal-700 mb-4">
                  Résultats pour "{word}"
                </h2>
                <ul className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                  {currentResults.map((result) => (
                    <li
                      key={result.id}
                      className="p-6 bg-white bg-opacity-90 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
                    >
                      <div className="flex flex-col space-y-2">
                        <div className="flex justify-between items-center">
                          <h3 className="text-lg font-semibold text-teal-700">
                            {result.title}
                          </h3>
                          <span className="text-sm text-teal-500">({result.language})</span>
                        </div>
                        <p className="text-sm text-gray-600">Auteur: {result.authors[0]?.name || 'Inconnu'}</p>
                        <p className="text-sm text-gray-500">Occurrences: {result.occurrences}</p>
                        <p className="text-sm text-gray-500">Score: {result.score.toFixed(2)}</p>
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
                {/* Contrôles de pagination pour les résultats */}
                <div className="mt-6 flex justify-center items-center space-x-4">
                  <button
                    onClick={handlePrevious}
                    disabled={currentPage === 1}
                    className="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300"
                  >
                    Précédent
                  </button>
                  <span className="text-teal-700 font-medium">
                    Page {currentPage} / {totalPages}
                  </span>
                  <button
                    onClick={handleNext}
                    disabled={currentPage === totalPages}
                    className="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300"
                  >
                    Suivant
                  </button>
                </div>
              </>
            )}
            {/* Section pour les suggestions */}
            {suggestions.length > 0 && (
              <>
                <h2 className="text-2xl font-semibold text-teal-700 mb-4 mt-8">
                  Suggestions similaires pour "{word}"
                </h2>
                <ul className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                  {suggestions.map((suggestion) => (
                    <li
                      key={suggestion.id}
                      className="p-6 bg-white bg-opacity-90 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
                    >
                      <div className="flex flex-col space-y-2">
                        <div className="flex justify-between items-center">
                          <h3 className="text-lg font-semibold text-teal-700">
                            {suggestion.title}
                          </h3>
                          <span className="text-sm text-teal-500">({suggestion.language})</span>
                        </div>
                        <p className="text-sm text-gray-600">Auteur: {suggestion.authors[0]?.name || 'Inconnu'}</p>
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
              </>
            )}
          </div>
        ) : (
          <p className="text-center text-gray-700">
            Aucune suggestion trouvée pour "{word}". Essayez une autre recherche.
          </p>
        )}
      </main>
    </div>
  );
};

export default SearchSuggestions;