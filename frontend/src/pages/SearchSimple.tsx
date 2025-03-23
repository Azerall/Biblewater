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
  score: number;
  occurrences: number;
  cover_url: string;
}

const SearchSimple: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [word, setWord] = useState<string>('');
  const [searchType, setSearchType] = useState<string>('Recherche');
  const [rankingType, setRankingType] = useState<string>('occurrences');
  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [itemsPerPage] = useState<number>(9);
  const location = useLocation();
  const navigate = useNavigate();
  const isInitialMount = useRef(true); 

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const q = params.get('query') || '';

    if (isInitialMount.current && q) {
      setQuery(q);
      handleSearch(q);
      isInitialMount.current = false;
    }
  }, [location.search]);

  const handleSearch = async (searchQuery: string) => {
    setLoading(true);
    try {
      const decodedQuery = decodeURIComponent(searchQuery);
      // Ré-encoder correctement après avoir mis en minuscules
      const encodedQuery = encodeURIComponent(decodedQuery.toLowerCase());
      console.log("Encoded query:", encodedQuery);
      console.log("API URL:", `${API_BASE_URL}/search/${encodedQuery}/`);
      const response = await fetch(`${API_BASE_URL}/search/${encodedQuery}/`);
      if (!response.ok) {
        throw new Error('Erreur lors de la recherche');
      }
      const data: Result[] = await response.json();
      setResults(data);
      setWord(searchQuery);
      setQuery(''); 
      setCurrentPage(1);
    } catch (err) {
      console.error(err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewSearch = () => {
    if (query.trim()) {
      if (searchType === 'Recherche') {
        handleSearch(query);
      }

      const basePath =
        searchType === 'Recherche'
          ? `/Biblewater/search`
          : searchType === 'Recherche avancée'
          ? `/Biblewater/advanced`
          : searchType === 'Classement'
          ? `/Biblewater/ranking`
          : searchType === 'Suggestions'
          ? `/Biblewater/suggestions`
          : '/Biblewater/';

      const params = new URLSearchParams();
      params.append('query', encodeURIComponent(query));
      if (searchType === 'Classement') {
        params.append('ranking', encodeURIComponent(rankingType));
      }

      const path = `${basePath}?${params.toString()}`;
      navigate(path, { replace: true }); 
    }
  };

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentResults = results.slice(indexOfFirstItem, indexOfLastItem);

  const totalPages = Math.ceil(results.length / itemsPerPage);

  const handlePrevious = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  return (
    <div className="min-h-screen">
      <header className="py-10 text-center">
        <h1 className="text-4xl font-extrabold text-teal-600 animate-bounce">
          Recherche Simple
        </h1>
      </header>
      <div className="sticky py-4">
        <div className="container mx-auto px-6">
          <div className="flex justify-center">
            <div className="w-full max-w-lg space-y-4">
            <div className="relative max-w-3xl mx-auto">
              <div className="flex flex-col md:flex-row items-center w-full space-y-2 md:space-y-0 md:space-x-2">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Entrez votre recherche..."
                  className="w-full p-4 text-lg bg-white border-2 border-teal-200 rounded-xl shadow-sm focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-300 transition-all duration-300 md:pr-40" // Ajusté pour une meilleure compatibilité avec la largeur du select
                />
                <select
                  value={searchType}
                  onChange={(e) => setSearchType(e.target.value)}
                  className="w-full md:w-32 p-2 md:p-3 bg-teal-500 text-white rounded-lg shadow-md focus:outline-none focus:ring-2 focus:ring-teal-300 hover:bg-teal-600 transition-all duration-300 md:absolute md:right-4 md:top-1/2 md:transform md:-translate-y-1/2" // Ajusté right-4 et w-32 pour un meilleur centrage
                >
                  <option value="Recherche">Recherche</option>
                  <option value="Recherche avancée">Recherche avancée</option>
                  <option value="Classement">Classement</option>
                  <option value="Suggestions">Suggestions</option>
                </select>
              </div>
            </div>
              {searchType === 'Classement' && (
                <div className="flex justify-center flex-col md:flex-row md:space-x-8 space-y-4 md:space-y-0">
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
                  to="/Biblewater/"
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
          <p className="text-center text-gray-700">Chargement des résultats...</p>
        ) : results.length > 0 ? (
            <div className="mt-12 max-w-5xl mx-auto">
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
                    {/* Adjusted cover image size */}
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
                      to={`/Biblewater/book/${result.id}`}
                      state={{
                        searchQuery: word,
                        searchType: 'simple',
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
          </div>
        ) : (
          <p className="text-center text-gray-700">Aucun résultat trouvé pour "{word}". Essayez une autre recherche.</p>
        )}
      </main>
    </div>
  );
};

export default SearchSimple;