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
  content: string;
  score: number;
  occurrences: number;
  closeness: number;
  betweenness: number;
  pagerank: number;
}

const SearchRanking: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [words, setWords] = useState<string>('');
  const [rankingType, setRankingType] = useState<string>('occurrences'); // Critère sélectionné par l'utilisateur
  const [lastRankingType, setLastRankingType] = useState<string>('occurrences'); // Critère utilisé pour la dernière recherche réussie
  const [results, setResults] = useState<Result[]>([]);
  const [searchType, setSearchType] = useState<string>('Classement');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1); // Page actuelle
  const [itemsPerPage] = useState<number>(9); // 9 livres par page
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const q = params.get('query') || '';
    setQuery(q);
  }, [location.search]);

  const handleSearch = async (searchQuery: string, ranking: string) => {
    setLoading(true);
    setError(null);
    try {
      if (!searchQuery.trim()) {
        throw new Error('La requête ne peut pas être vide.');
      }

      const response = await fetch(`http://127.0.0.1:8000/gutenberg/search_with_ranking/${encodeURIComponent(searchQuery)}/${encodeURIComponent(ranking)}/`);
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status} - ${response.statusText}`);
      }
      const data = await response.json();
      if (!data.results || !Array.isArray(data.results)) {
        throw new Error('Réponse inattendue du serveur.');
      }
      console.log("=============shibal ranking==================");
      setResults(data.results);
      setLastRankingType(ranking); // Met à jour lastRankingType après une recherche réussie
      setWords(searchQuery);
      setQuery('');
      setCurrentPage(1); // Réinitialiser la page à 1 après une nouvelle recherche
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Aucun résultat trouvé ou une erreur est survenue. Veuillez réessayer.'
      );
      console.error('Erreur détaillée:', err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewSearch = async () => {
    if (query.trim()) {
      if (searchType === 'Classement') {
        await handleSearch(query, rankingType); // Exécute la recherche directement
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

  // Calculer les indices pour la pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentResults = results.slice(indexOfFirstItem, indexOfLastItem);

  // Calculer le nombre total de pages
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
          Classement des Résultats
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
          <p className="text-center text-gray-700">Chargement des résultats...</p>
        ) : results.length > 0 ? (
          <>
            <h2 className="text-2xl font-semibold text-teal-700 mb-4">
              Résultats pour "{words}" triés par {lastRankingType}
            </h2>
            <ul className="mt-12 max-w-5xl mx-auto grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
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
                    <p className="text-sm text-gray-500">
                      {result.content ? (result.content.length > 20
                        ? `${result.content.slice(0, 20)}...`
                        : result.content) : 'Aucun extrait disponible'}
                    </p>
                    <p className="text-sm text-gray-600">Auteur: {result.authors[0]?.name || 'Inconnu'}</p>
                    {lastRankingType === 'occurrences' && (
                      <p className="text-sm text-gray-500">Occurrences: {result.occurrences}</p>
                    )}
                    {lastRankingType === 'closeness' && (
                      <p className="text-sm text-gray-500">Closeness: {result.closeness.toFixed(2)}</p>
                    )}
                    {lastRankingType === 'betweenness' && (
                      <p className="text-sm text-gray-500">Betweenness: {result.betweenness.toFixed(2)}</p>
                    )}
                    {lastRankingType === 'pagerank' && (
                      <p className="text-sm text-gray-500">PageRank: {result.pagerank.toFixed(2)}</p>
                    )}
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
            {/* Contrôles de pagination simplifiés */}
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
        ) : (
          <p className="text-center text-gray-700">Aucun résultat trouvé pour "{query}". Essayez une autre recherche.</p>
        )}
      </main>
    </div>
  );
};

export default SearchRanking;