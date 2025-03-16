import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Home: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [searchType, setSearchType] = useState<string>('Recherche');
  const navigate = useNavigate();

  const handleSearch = () => {
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
    // <div className="min-h-screen bg-gradient-to-t from-teal-50 to-yellow-50 flex flex-col items-center justify-center">
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