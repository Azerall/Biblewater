import { useState } from 'react';

const MobileHome: React.FC = () => {
  const [query, setQuery] = useState<string>('');

  return (
    <div className="min-h-screen bg-gray-100 max-w-md mx-auto">
      <header className="flex items-center p-4 bg-white border-b">
        <span className="text-xl">☰</span>
        <h1 className="flex-1 text-center text-lg font-bold">Bibliothèque</h1>
      </header>
      <main className="flex flex-col items-center p-6">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Mot-clé ou RegEx"
          className="w-4/5 p-2 border rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <div className="mt-6 flex flex-col gap-4 w-4/5">
          <button className="bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600">
            Recherche Simple
          </button>
          <button className="bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600">
            Recherche Avancée
          </button>
        </div>
      </main>
    </div>
  );
};

export default MobileHome;