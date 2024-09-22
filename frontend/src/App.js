import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import PaintingDetails from './components/PaintingDetails';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/painting/:uniqueFilename" element={<PaintingDetails />} />
      </Routes>
    </Router>
  );
}

export default App;
