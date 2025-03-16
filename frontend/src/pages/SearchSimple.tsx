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
}

const SearchSimple: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [searchType, setSearchType] = useState<string>('Recherche');
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
    const mockResults = [
      { id: 1, title: 'Livre 1', authors: [{ name: 'Auteur 1' }], language: 'fr', content: 'Un extrait de contenu...' },
      { id: 2, title: 'Livre 2', authors: [{ name: 'Author 2' }], language: 'en', content: 'Un autre extrait de contenu...' },
      { id: 3, title: 'Élément 3', authors: [{ name: 'Auteur 3' }], language: 'fr', content: 'Un exemple de contenu pertinent...' },
      { id: 4, title: 'Livre 4', authors: [{ name: 'Author 4' }], language: 'en', content: 'Un autre exemple de contenu pertinent...' },
      { id: 5, title: 'Résumé 5', authors: [{ name: 'Auteur 5' }], language: 'fr', content: 'Un résumé trouvé...' },
      { id: 6, title: 'Livre 6', authors: [{ name: 'Author 6' }], language: 'en', content: 'Un autre exemple de contenu trouvé...' },
      { id: 7, title: 'Mot-clé trouvé', authors: [{ name: 'Auteur 7' }], language: 'fr', content: 'Mot-clé trouvé dans ce contexte...' },
      { id: 8, title: 'Livre 8', authors: [{ name: 'Author 8' }], language: 'en', content: 'Mot-clé trouvé dans un autre contexte...' },
      { id: 9, title: 'Dernier Résultat', authors: [{ name: 'Auteur 9' }], language: 'fr', content: 'Dernier exemple de résultat...' },
      { id: 10, title: 'Résumé Étendu', authors: [{ name: 'Author 10' }], language: 'en', content: 'Dernier exemple de résultat trouvé...' },
      { id: 11, title: 'Résumé Pertinent', authors: [{ name: 'Auteur 11' }], language: 'fr', content: 'Dernier exemple de résultat pertinent...' },
      { id: 12, title: 'Résumé Avancé', authors: [{ name: 'Author 12' }], language: 'en', content: 'Dernier exemple de résultat pertinent trouvé...' },
      { id: 13, title: 'Résumé Contextuel', authors: [{ name: 'Auteur 13' }], language: 'fr', content: 'Dernier exemple de résultat trouvé dans ce contexte...' },
      { id: 14, title: 'Tést Accentué', authors: [{ name: 'Auteur 14' }], language: 'fr', content: 'Test avec des accents...' },
      { id: 15, title: 'Résumé Étranger', authors: [{ name: 'Auteur 15' }], language: 'fr', content: 'Résumé avec des caractères spéciaux...' },
    ].filter((r) =>
      r.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.title.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Tri par défaut (pas d'occurrences, donc on peut trier par titre ou autre logique)
    const sortedResults = [...mockResults].sort((a, b) => a.title.localeCompare(b.title));
    setResults(sortedResults);

    const topIds = sortedResults.slice(0, 2).map((r) => r.id);
    const mockSuggestions = [
      { id: 16, title: 'Livre 16', authors: [{ name: 'Auteur 16' }], language: 'fr', content: 'Suggestion liée...' },
      { id: 17, title: 'Livre 17', authors: [{ name: 'Author 17' }], language: 'en', content: 'Autre suggestion...' },
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
    // <div className="min-h-screen bg-gradient-to-t from-teal-50 to-yellow-50">
    <div className="min-h-screen">
      <header className="py-10 text-center">
        <h1 className="text-4xl font-extrabold text-teal-600 animate-bounce">
          Recherche Simple
        </h1>
      </header>
      {/* <div className="sticky bg-gradient-to-t from-teal-50 to-yellow-50 py-4"> */}
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
                      {result.content.length > 20 ? `${result.content.slice(0, 20)}...` : result.content}
                    </p>
                    <p className="text-sm text-gray-600">Auteur: {result.authors[0]?.name || 'Inconnu'}</p>
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
                      className="p-6 bg-white bg-opacity-90 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
                    >
                      <div className="flex flex-col space-y-2">
                        <div className="flex justify-between items-center">
                          <h3 className="text-lg font-semibold text-teal-700">
                            {suggestion.title}
                          </h3>
                          <span className="text-sm text-teal-500">({suggestion.language})</span>
                        </div>
                        <p className="text-sm text-gray-500">
                          {suggestion.content.length > 20
                            ? `${suggestion.content.slice(0, 20)}...`
                            : suggestion.content}
                        </p>
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

export default SearchSimple;