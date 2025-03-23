import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Home: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [searchType, setSearchType] = useState<string>('Recherche');
  const [rankingType, setRankingType] = useState<string>('occurrences'); 
  const navigate = useNavigate();

  const handleSearch = () => {
    if (query.trim()) {
      const basePath = searchType === 'Recherche'
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
      navigate(path);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <header className="py-10 text-center">
        <h1 className="text-5xl font-extrabold text-teal-600 animate-bounce">
          Biblewater
        </h1>
        <p className="mt-4 text-lg text-teal-700">
          Explorez plus de 1664 livres avec facilité
        </p>
      </header>
      <main className="container mx-auto px-6 py-12 flex-grow flex items-center justify-center">
        <div className="w-full max-w-lg space-y-6">
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
            onClick={handleSearch}
            className="w-full px-8 py-4 bg-teal-600 text-white font-bold rounded-xl shadow-md hover:bg-teal-700 hover:rotate-2 transition-all duration-300"
          >
            Rechercher
          </button>
        </div>
      </main>
      <footer className="text-center py-8">
        <p className="text-teal-600">
          Une application pour découvrir et lire vos livres préférés
        </p>
      </footer>
    </div>
  );
};

export default Home;