import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SearchSimple from './pages/SearchSimple';
import SearchAdvanced from './pages/SearchAdvanced';
import SearchRanking from './pages/SearchRanking';
import SearchSuggestions from './pages/SearchSuggestions';
import Book from './pages/Book';
import Home from './pages/Home';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/Biblewater/" element={<Home />} />
        <Route path="/Biblewater/search" element={<SearchSimple />} />
        <Route path="/Biblewater/advanced" element={<SearchAdvanced />} />
        <Route path="/Biblewater/ranking" element={<SearchRanking />} />
        <Route path="/Biblewater/suggestions" element={<SearchSuggestions />} />
        <Route path="/Biblewater/book/:id" element={<Book />} />
      </Routes>
    </Router>
  );
};

export default App;