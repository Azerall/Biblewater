import { useParams, Link } from 'react-router-dom';

interface BookData {
  id: number;
  title: string;
  language: string;
  content: string;
}

const Book: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const mockBooks: BookData[] = [
    { id: 1, title: 'Livre 1', language: 'fr', content: 'Un extrait de contenu... Voici le texte complet du Livre 1, avec beaucoup de mots pour montrer ce que ça donne sur une page entière.' },
    { id: 2, title: 'Livre 2', language: 'en', content: 'Another excerpt... This is the full text of Book 2, filled with interesting details and a longer narrative.' },
    { id: 3, title: 'Livre 3', language: 'fr', content: 'Un exemple de contenu pertinent... Le texte intégral du Livre 3, avec des descriptions et des paragraphes.' },
    { id: 4, title: 'Livre 4', language: 'en', content: 'Another pertinent excerpt... Full content of Book 4, ready to be read in its entirety.' },
    { id: 5, title: 'Livre 5', language: 'fr', content: 'Un exemple de contenu trouvé... Voici tout le Livre 5, un long texte captivant.' },
    { id: 6, title: 'Livre 6', language: 'en', content: 'Another found excerpt... The entire Book 6, with plenty of text to explore.' },
    { id: 7, title: 'Livre 7', language: 'fr', content: 'Mot-clé trouvé dans ce contexte... Le Livre 7 en entier, avec des détails riches.' },
    { id: 8, title: 'Livre 8', language: 'en', content: 'Keyword in another context... Full text of Book 8, a complete story.' },
    { id: 9, title: 'Livre 9', language: 'fr', content: 'Dernier exemple de résultat... Texte complet du Livre 9, prêt à être lu.' },
    { id: 10, title: 'Livre 10', language: 'en', content: 'Last result excerpt... The whole Book 10, an engaging read.' },
    { id: 11, title: 'Livre 11', language: 'fr', content: 'Dernier exemple pertinent... Livre 11 en entier, avec un contenu détaillé.' },
    { id: 12, title: 'Livre 12', language: 'en', content: 'Last pertinent result... Full Book 12, a complete narrative.' },
    { id: 13, title: 'Livre 13', language: 'fr', content: 'Dernier résultat dans ce contexte... Texte intégral du Livre 13.' },
  ];

  const book = mockBooks.find((b) => b.id === Number(id));

  if (!book) {
    return (
      <div className="min-h-screen bg-gradient-to-t from-teal-50 to-yellow-50 flex items-center justify-center">
        <p className="text-xl text-gray-700">Livre non trouvé</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-t from-teal-50 to-yellow-50">
      <header className="py-10 text-center">
        <h1 className="text-4xl font-extrabold text-teal-600">
          {book.title}
        </h1>
        <p className="text-sm text-teal-500 mt-2">Langue : {book.language}</p>
      </header>
      <main className="container mx-auto px-6 py-12">
        <div className="max-w-3xl mx-auto bg-white p-8 rounded-xl shadow-lg">
          <p className="text-gray-700 leading-relaxed">{book.content}</p>
        </div>
        <div className="text-center mt-8">
          <Link
            to="/"
            className="text-teal-600 hover:text-teal-800 font-semibold transition-colors duration-300"
          >
            Retour à la recherche
          </Link>
        </div>
      </main>
    </div>
  );
};

export default Book;