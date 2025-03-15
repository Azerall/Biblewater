interface Result {
    id: number;
    title: string;
    excerpt: string;
  }
  
  interface Suggestion {
    id: number;
    title: string;
  }
  
  const MobileResults: React.FC = () => {
    const results: Result[] = [
      { id: 1, title: 'Livre 1', excerpt: 'Extrait ici...' },
      { id: 2, title: 'Livre 2', excerpt: 'Un autre...' },
    ];
    const suggestions: Suggestion[] = [
      { id: 3, title: 'Livre Similaire 1' },
      { id: 4, title: 'Livre Populaire 2' },
    ];
  
    return (
      <div className="min-h-screen bg-gray-100 max-w-md mx-auto">
        <header className="p-4 bg-white border-b">
          <input
            type="text"
            defaultValue="mot-clé"
            className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </header>
        <main className="p-4">
          <ul>
            {results.map((result) => (
              <li key={result.id} className="p-2 bg-white rounded-md mb-2 shadow-sm">
                {result.title} - {result.excerpt}
              </li>
            ))}
          </ul>
          <hr className="my-4 border-gray-300" />
          <h3 className="text-lg font-semibold">Suggestions</h3>
          <ul>
            {suggestions.map((suggestion) => (
              <li
                key={suggestion.id}
                className="p-2 italic text-gray-700 bg-white rounded-md mb-2 shadow-sm"
              >
                {suggestion.title}
              </li>
            ))}
          </ul>
        </main>
      </div>
    );
  };
  
  export default MobileResults;