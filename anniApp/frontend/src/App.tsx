import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Welcome from './pages/Welcome';
import VotingPage from './pages/VotingPage';
import MessagePage from './pages/MessagePage';
import ThankYou from './pages/ThankYou';
import AdminResults from './pages/AdminResults';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/vote/:activityNumber" element={<VotingPage />} />
        <Route path="/message" element={<MessagePage />} />
        <Route path="/thank-you" element={<ThankYou />} />
        <Route path="/anniversary-celebration-results" element={<AdminResults />} />
      </Routes>
    </Router>
  );
}

export default App;
