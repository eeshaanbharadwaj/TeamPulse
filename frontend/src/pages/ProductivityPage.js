// frontend/src/pages/ProductivityPage.js
import React, { useState, useEffect } from 'react';
import api from '../api/axiosConfig';
import ProductivityBar from '../components/ProductivityBar'; // <-- Import the new component

const ProductivityPage = () => {
  const [developers, setDevelopers] = useState([]);
  const [scores, setScores] = useState({}); 
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTeamData = async () => {
      try {
        const devResponse = await api.get('/developers/');
        const devList = devResponse.data;
        setDevelopers(devList);

        // Fetch the Productivity Score for EACH developer
        const scorePromises = devList.map(dev => 
          api.get(`/productivity/${dev.id}/`) // Fetch prediction from new endpoint
            .then(res => ({ id: dev.id, scoreData: res.data }))
            .catch(() => ({ id: dev.id, scoreData: { score: 'N/A', status: 'Error' } })) 
        );

        const scoreResults = await Promise.all(scorePromises);
        const scoresMap = scoreResults.reduce((acc, curr) => {
          acc[curr.id] = curr.scoreData;
          return acc;
        }, {});

        setScores(scoresMap);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching productivity data:", err);
        setError("Failed to fetch productivity data from the backend API.");
        setLoading(false);
      }
    };

    fetchTeamData();
  }, []); 

  if (loading) return <h2>Loading Productivity Metrics...</h2>;
  if (error) return <h2 style={{color: 'red'}}>{error}</h2>;

  // Simple styles
  const tableHeaderStyle = { border: '1px solid #ddd', padding: '12px', textAlign: 'left', backgroundColor: '#e9ecef' };
  const tableCellStyle = { border: '1px solid #ddd', padding: '8px' };

  return (
    <div style={{ fontFamily: 'Arial' }}>
      <h2>📈 Developer Productivity Score</h2>
      <p>Score based on Commits (lines changed) and Jira Throughput (high-value tickets).</p>

      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9em', marginTop: '20px' }}>
        <thead>
          <tr>
            <th style={tableHeaderStyle}>Developer Name</th>
            <th style={{...tableHeaderStyle, width: '40%'}}>Productivity Score</th>
            <th style={tableHeaderStyle}>Status</th>
            <th style={tableHeaderStyle}>Features (Raw Data)</th>
          </tr>
        </thead>
        <tbody>
          {developers.map(dev => {
            const scoreData = scores[dev.id] || {};
            const score = typeof scoreData.score === 'number' ? scoreData.score : 0;

            const statusColor = score >= 80 ? 'green' : score >= 50 ? 'orange' : 'red';
            const features = scoreData.features || {};

            return (
              <tr key={dev.id}>
                <td style={tableCellStyle}>{dev.name}</td>
                <td style={tableCellStyle}>
                  <ProductivityBar developerName={dev.name} score={score} />
                </td>
                <td style={{ ...tableCellStyle, color: statusColor, fontWeight: 'bold' }}>{scoreData.status}</td>
                <td style={tableCellStyle}>
                    Lines: {features.total_lines_changed || 0} | Tickets: {features.high_value_tickets_closed || 0}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default ProductivityPage;
