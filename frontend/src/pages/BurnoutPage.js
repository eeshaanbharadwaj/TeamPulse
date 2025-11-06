// frontend/src/pages/BurnoutPage.js
import React from 'react';
import DeveloperList from '../components/DeveloperList'; // Reuse our existing component

const BurnoutPage = () => {
  return (
    <div>
      <h2>🔥 Burnout Risk Analysis</h2>
      <p>Developer activity metrics fed into the scikit-learn classification model.</p>
      <DeveloperList /> {/* Display the risk scores here */}
    </div>
  );
};
export default BurnoutPage;