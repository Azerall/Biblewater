import { useState, useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import noCoverImage from '../assets/no_cover.png';
import { API_BASE_URL } from '../utils/apiUtils';

interface Author {
  name: string;
}

interface Result {
  id: number;
  title: string;
  authors: Author[];
  language: string;
  cover_url: string;
  score: number;
  occurrences: number;
}

interface Suggestion {
  id: number;
  title: string;
  authors: Author[];
  language: string;
  cover_url: string;
}

interface SuggestionResponse {
  results: Result[];
  suggestions: Suggestion[];
}

const SearchSuggestions: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [word, setWord] = useState<string>(''); 
  const [searchType, setSearchType] = useState<string>('Suggestions');
  const [rankingType, setRankingType] = useState<string>('occurrences'); 
  const [results, setResults] = useState<Result[]>([]); 
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [currentPage, setCurrentPage] = useState<number>(1); 
  const [currentSuggestionsPage, setCurrentSuggestionsPage] = useState<number>(1); 
  const [itemsPerPage] = useState<number>(9); 
  const location = useLocation();
  const navigate = useNavigate();
  const isInitialMount = useRef(true); 

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const q = params.get('query') || '';

    if (isInitialMount.current && q) {
      setQuery(q);
      fetchSuggestions(q);
      isInitialMount.current = false; 
    }
  }, [location.search]);

  const fetchSuggestions = async (searchQuery: string) => {
    setLoading(true);
    try {
      if (!searchQuery.trim()) {
        throw new Error('La requête ne peut pas être vide.');
      }

      const response = await fetch(`${API_BASE_URL}/search_with_suggestions/${encodeURIComponent(searchQuery)}/`);
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status} - ${response.statusText}`);
      }
      const data: SuggestionResponse = await response.json();
      console.log("======= suggestions data =======", data);

      const suggestionIds = new Set(data.suggestions.map(suggestion => suggestion.id));
      const filteredResults = data.results.filter(result => !suggestionIds.has(result.id));

      setResults(filteredResults || []);
      setSuggestions(data.suggestions || []);
      setWord(searchQuery);
      setQuery(''); 
      setCurrentPage(1); 
      setCurrentSuggestionsPage(1); 
    } catch (err) {
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
        await fetchSuggestions(query);
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
        params.append('ranking', encodeURIComponent(rankingType)); 
      }

      const path = `${basePath}?${params.toString()}`;
      navigate(path, { replace: true }); 
    }
  };

  const indexOfLastResult = currentPage * itemsPerPage;
  const indexOfFirstResult = indexOfLastResult - itemsPerPage;
  const currentResults = results.slice(indexOfFirstResult, indexOfLastResult);

  const totalResultPages = Math.ceil(results.length / itemsPerPage);

  const indexOfLastSuggestion = currentSuggestionsPage * itemsPerPage;
  const indexOfFirstSuggestion = indexOfLastSuggestion - itemsPerPage;
  const currentSuggestions = suggestions.slice(indexOfFirstSuggestion, indexOfLastSuggestion);

  const totalSuggestionPages = Math.ceil(suggestions.length / itemsPerPage);

  const handlePreviousResult = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextResult = () => {
    if (currentPage < totalResultPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handlePreviousSuggestion = () => {
    if (currentSuggestionsPage > 1) {
      setCurrentSuggestionsPage(currentSuggestionsPage - 1);
    }
  };

  const handleNextSuggestion = () => {
    if (currentSuggestionsPage < totalSuggestionPages) {
      setCurrentSuggestionsPage(currentSuggestionsPage + 1);
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
              <div className="relative max-w-3xl mx-auto">
                <div className="relative flex items-center w-full">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Entrez votre recherche..."
                    className="w-full p-4 pr-36 text-lg bg-white border-2 border-teal-200 rounded-xl shadow-sm focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-300 transition-all duration-300"
                  />
                  <select
                    value={searchType}
                    onChange={(e) => setSearchType(e.target.value)}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 bg-teal-500 text-white rounded-lg shadow-md focus:outline-none focus:ring-2 focus:ring-teal-300 hover:bg-teal-600 transition-all duration-300"
                  >
                    <option value="Recherche">Recherche</option>
                    <option value="Recherche avancée">Recherche avancée</option>
                    <option value="Classement">Classement</option>
                    <option value="Suggestions">Suggestions</option>
                  </select>
                </div>
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
        {loading ? (
          <p className="text-center text-gray-700">Chargement des suggestions...</p>
        ) : results.length > 0 || suggestions.length > 0 ? (
          <div className="mt-12 max-w-5xl mx-auto">
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
                        <div className="w-32 h-48 mx-auto mb-4">
                          <img
                            src={result.cover_url}
                            alt={`Cover of ${result.title}`}
                            className="object-cover rounded-md"
                            loading="lazy"
                            onError={(e) => {
                              e.currentTarget.src = noCoverImage;
                            }}
                          />
                        </div>
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
                          state={{
                            searchQuery: word,
                            searchType: 'suggestions', 
                          }}
                          className="text-yellow-500 hover:text-yellow-600 font-medium text-right"
                        >
                          Lire
                        </Link>
                      </div>
                    </li>
                  ))}
                </ul>
                <div className="mt-6 flex justify-center items-center space-x-4">
                  <button
                    onClick={handlePreviousResult}
                    disabled={currentPage === 1}
                    className="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300"
                  >
                    Précédent
                  </button>
                  <span className="text-teal-700 font-medium">
                    Page {currentPage} / {totalResultPages}
                  </span>
                  <button
                    onClick={handleNextResult}
                    disabled={currentPage === totalResultPages}
                    className="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300"
                  >
                    Suivant
                  </button>
                </div>
              </>
            )}
            {suggestions.length > 0 && (
              <>
                <h2 className="text-2xl font-semibold text-teal-700 mb-4 mt-8">
                  Suggestions similaires pour "{word}"
                </h2>
                <ul className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                  {currentSuggestions.map((suggestion) => (
                    <li
                      key={suggestion.id}
                      className="p-6 bg-white bg-opacity-90 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
                    >
                      <div className="flex flex-col space-y-2">
                        <div className="w-32 h-48 mx-auto mb-4">
                          <img
                            src={suggestion.cover_url}
                            alt={`Cover of ${suggestion.title}`}
                            className="object-cover rounded-md"
                            loading="lazy"
                            onError={(e) => {
                              e.currentTarget.src = noCoverImage;
                            }}
                          />
                        </div>
                        <div className="flex justify-between items-center">
                          <h3 className="text-lg font-semibold text-teal-700">
                            {suggestion.title}
                          </h3>
                          <span className="text-sm text-teal-500">({suggestion.language})</span>
                        </div>
                        <p className="text-sm text-gray-600">Auteur: {suggestion.authors[0]?.name || 'Inconnu'}</p>
                        <Link
                          to={`/book/${suggestion.id}`}
                          state={{
                            searchQuery: word,
                            searchType: 'suggestions', 
                          }}
                          className="text-yellow-500 hover:text-yellow-600 font-medium text-right"
                        >
                          Lire
                        </Link>
                      </div>
                    </li>
                  ))}
                </ul>
                <div className="mt-6 flex justify-center items-center space-x-4">
                  <button
                    onClick={handlePreviousSuggestion}
                    disabled={currentSuggestionsPage === 1}
                    className="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300"
                  >
                    Précédent
                  </button>
                  <span className="text-teal-700 font-medium">
                    Page {currentSuggestionsPage} / {totalSuggestionPages}
                  </span>
                  <button
                    onClick={handleNextSuggestion}
                    disabled={currentSuggestionsPage === totalSuggestionPages}
                    className="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300"
                  >
                    Suivant
                  </button>
                </div>
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