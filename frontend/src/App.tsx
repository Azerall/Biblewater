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
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<SearchSimple />} />
        <Route path="/advanced" element={<SearchAdvanced />} />
        <Route path="/ranking" element={<SearchRanking />} />
        <Route path="/suggestions" element={<SearchSuggestions />} />
        <Route path="/book/:id" element={<Book />} />
      </Routes>
    </Router>
  );
};

export default App;