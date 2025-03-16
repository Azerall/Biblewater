import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SearchSimple from './pages/SearchSimple';
import SearchAdvanced from './pages/SearchAdvanced';
import MobileHome from './pages/MobileHome';
import MobileResults from './pages/MobileResults';
import Dashboard from './pages/Dashboard';
import Book from './pages/Book'; // Import de la page Book

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SearchSimple />} />
        <Route path="/advanced" element={<SearchAdvanced />} />
        <Route path="/mobile-home" element={<MobileHome />} />
        <Route path="/mobile-results" element={<MobileResults />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/book/:id" element={<Book />} /> {/* Nouvelle route */}
      </Routes>
    </Router>
  );
};

export default App;