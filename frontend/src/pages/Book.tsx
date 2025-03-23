import { useState, useEffect } from 'react';
import { Link, useParams, useLocation, useNavigate } from 'react-router-dom';
import noCoverImage from '../assets/no_cover.png';
import back_bouton from '../assets/bouton_back.png';

interface Author {
  name: string;
}

interface BookData {
  id: number;
  title: string;
  authors: Author[];
  language: string;
  cover_url: string;
  content: string;
}

const Book: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const [book, setBook] = useState<BookData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Récupérer les informations depuis l'état
  const { searchQuery, searchType, rankingType } = (location.state as {
    searchQuery?: string;
    searchType?: string;
    rankingType?: string;
  }) || {};

  // Construire l'URL de retour en fonction du type de recherche
  let returnUrl = '/Biblewater/'; // Par défaut, retourner à la page d'accueil
  let searchTypeLabel = 'recherche'; // Étiquette pour le type de recherche
  if (searchQuery && searchType) {
    const params = new URLSearchParams();
    params.append('query', encodeURIComponent(searchQuery));

    if (searchType === 'ranking' && rankingType) {
      params.append('ranking', encodeURIComponent(rankingType));
    }

    const basePath =
      searchType === 'simple'
        ? '/Biblewater/search'
        : searchType === 'advanced'
        ? '/Biblewater/advanced'
        : searchType === 'ranking'
        ? '/Biblewater/ranking'
        : searchType === 'suggestions'
        ? '/Biblewater/suggestions'
        : '/Biblewater/';

    returnUrl = `${basePath}?${params.toString()}`;

    // Définir une étiquette pour le type de recherche
    searchTypeLabel =
      searchType === 'simple'
        ? 'recherche simple'
        : searchType === 'advanced'
        ? 'recherche avancée'
        : searchType === 'ranking'
        ? 'classement'
        : searchType === 'suggestions'
        ? 'suggestions'
        : 'recherche';
  }

  useEffect(() => {
    const fetchBook = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://127.0.0.1:8000/gutenberg/book/${id}/`);
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('Livre non trouvé');
          }
          throw new Error('Erreur lors de la récupération du livre');
        }
        const data: BookData = await response.json();
        setBook(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Une erreur est survenue');
        setBook(null);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchBook();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-xl text-gray-700">Chargement du livre...</p>
      </div>
    );
  }

  if (error || !book) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-xl text-gray-700">{error || 'Livre non trouvé'}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <header className="py-10 text-center relative">
        <h1 className="text-4xl font-extrabold text-teal-600">{book.title}</h1>
        <p className="text-xl text-teal-500 mt-2">Langue : {book.language}</p>
        <p className="text-xl text-teal-500 mt-1">
          Auteur : {book.authors[0]?.name || 'Inconnu'}
        </p>
      </header>
      <main className="container mx-auto px-6 py-12">
  {/* Appliquer max-w-3xl mx-auto pour aligner avec la zone de texte */}
  <div className="max-w-3xl mx-auto mb-6">
    <button
      onClick={() => navigate(returnUrl)}
      className="group flex items-center space-x-2 px-4 py-2 bg-white bg-opacity-20 backdrop-blur-md text-teal-600 font-semibold rounded-xl shadow-md hover:bg-opacity-30 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 transition-all duration-300"
    >
      <img
        src={back_bouton}
        alt="Retour"
        className="w-6 h-6 transform group-hover:-translate-x-1 transition-transform duration-300"
      />
      <span>Retour à la {searchTypeLabel} pour "{searchQuery || 'inconnu'}"</span>
    </button>

  </div>
  <div className="max-w-3xl mx-auto bg-white bg-opacity-90 p-8 rounded-xl shadow-lg">
    {/* Display the cover image */}
    <div className="w-32 h-48 mx-auto mb-6">
      <img
        src={book.cover_url}
        alt={`Cover of ${book.title}`}
        className="object-cover rounded-md"
        loading="lazy"
        onError={(e) => {
          e.currentTarget.src = noCoverImage;
        }}
      />
    </div>
    {/* Display the content */}
    <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
      {book.content}
    </div>
  </div>
  <div className="text-center mt-8">
    <Link
      to="/Biblewater/"
      className="text-teal-600 hover:text-teal-800 font-semibold transition-colors duration-300"
    >
      Retour à l’accueil
    </Link>
  </div>
</main>
    </div>
  );
};

export default Book;