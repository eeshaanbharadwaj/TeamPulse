// frontend/src/App.js
import React from 'react';
import { Routes, Route, Link } from 'react-router-dom'; // <-- Import routing components
import ProductivityPage from './pages/ProductivityPage';
import BurnoutPage from './pages/BurnoutPage';
import CollaborationPage from './pages/CollaborationPage';
import './App.css'; 

function App() {
  const linkStyle = { marginRight: '20px', textDecoration: 'none', color: '#007bff', fontWeight: 'bold' };

  return (
    <div className="App" style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>TeamPulse: Developer Productivity Intelligence</h1>
      
      {/* --- Navigation Bar --- */}
      <nav style={{ borderBottom: '1px solid #ccc', paddingBottom: '10px', marginBottom: '20px' }}>
        <Link to="/productivity" style={linkStyle}>Productivity</Link>
        <Link to="/burnout" style={linkStyle}>Burnout Risk</Link>
        <Link to="/collaboration" style={linkStyle}>Collaboration</Link>
      </nav>

      {/* --- Page Content --- */}
      <Routes>
        {/* Set Productivity as the default landing page */}
        <Route path="/" element={<ProductivityPage />} /> 
        <Route path="/productivity" element={<ProductivityPage />} />
        <Route path="/burnout" element={<BurnoutPage />} />
        <Route path="/collaboration" element={<CollaborationPage />} />
      </Routes>
    </div>
  );
}

export default App;