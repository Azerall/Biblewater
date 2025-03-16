import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SearchSimple from './pages/SearchSimple';
import SearchAdvanced from './pages/SearchAdvanced';
import SearchRanking from './pages/SearchRanking';
import SearchSuggestions from './pages/SearchSuggestions';
import MobileHome from './pages/MobileHome';
import MobileResults from './pages/MobileResults';
import Dashboard from './pages/Dashboard';
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
        <Route path="/mobile-home" element={<MobileHome />} />
        <Route path="/mobile-results" element={<MobileResults />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
};

export default App;