// frontend/src/components/DeveloperList.js
import React, { useState, useEffect } from 'react';
import api from '../api/axiosConfig';

const DeveloperList = () => {
  const [developers, setDevelopers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [risks, setRisks] = useState({}); // State to store all burnout risks

  useEffect(() => {
    const fetchTeamData = async () => {
      try {
        // 1. Fetch the list of all developers
        const devResponse = await api.get('/developers/');
        const devList = devResponse.data;
        setDevelopers(devList);

        // 2. Fetch the Burnout Risk for EACH developer
        const riskPromises = devList.map(dev => 
          api.get(`/burnout/${dev.id}/`) // Fetch prediction from new endpoint
            .then(res => ({ id: dev.id, risk: res.data }))
            .catch(() => ({ id: dev.id, risk: { risk_level: 'Error', risk_score: 'N/A' } })) // Handle API errors
        );
        
        const riskResults = await Promise.all(riskPromises);
        const risksMap = riskResults.reduce((acc, curr) => {
          acc[curr.id] = curr.risk;
          return acc;
        }, {});
        
        setRisks(risksMap);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to fetch team data from the backend API.");
        setLoading(false);
      }
    };

    fetchTeamData();
  }, []); 

  if (loading) return <h2>Loading TeamPulse Intelligence...</h2>;
  if (error) return <h2 style={{color: 'red'}}>{error}</h2>;

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>💡 TeamPulse Developer Intelligence</h1>
      <p>Data pulled from Django API and processed by scikit-learn model.</p>
      
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
        <thead>
          <tr style={{ backgroundColor: '#f2f2f2' }}>
            <th style={tableHeaderStyle}>Developer Name</th>
            <th style={tableHeaderStyle}>Burnout Risk (Score)</th>
            <th style={tableHeaderStyle}>Risk Level</th>
          </tr>
        </thead>
        <tbody>
          {developers.map(dev => {
            const riskData = risks[dev.id] || { risk_level: 'Loading...', risk_score: '...' };
            
            // Define color based on risk level (using the dummy logic for now)
            const riskColor = riskData.risk_level === 'High' ? 'red' : 
                              riskData.risk_level === 'Low' ? 'green' : 'black';

            return (
              <tr key={dev.id}>
                <td style={tableCellStyle}>{dev.name}</td>
                <td style={tableCellStyle}>{riskData.risk_score}%</td>
                <td style={{ ...tableCellStyle, color: riskColor, fontWeight: 'bold' }}>{riskData.risk_level}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

// Simple inline styles for the table
const tableHeaderStyle = { 
    border: '1px solid #ddd', 
    padding: '8px', 
    textAlign: 'left' 
};
const tableCellStyle = { 
    border: '1px solid #ddd', 
    padding: '8px' 
};

export default DeveloperList;