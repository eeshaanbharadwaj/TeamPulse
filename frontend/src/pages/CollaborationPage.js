// frontend/src/pages/CollaborationPage.js
import React, { useState, useEffect } from 'react';
import api from '../api/axiosConfig';
import CollaborationPie from '../components/CollaborationPie'; // <-- Import the new component

const CollaborationPage = () => {
  const [developers, setDevelopers] = useState([]);
  const [scores, setScores] = useState({}); 
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusCounts, setStatusCounts] = useState({});

  useEffect(() => {
    const fetchTeamData = async () => {
      try {
        const devResponse = await api.get('/developers/');
        const devList = devResponse.data;
        setDevelopers(devList);

        // Fetch the Collaboration Score for EACH developer
        const scorePromises = devList.map(dev => 
          api.get(`/collaboration/${dev.id}/`)
            .then(res => ({ id: dev.id, scoreData: res.data }))
            .catch(() => ({ id: dev.id, scoreData: { status: 'Error', score: 'N/A' } })) 
        );

        const scoreResults = await Promise.all(scorePromises);
        const scoresMap = scoreResults.reduce((acc, curr) => {
          acc[curr.id] = curr.scoreData;
          return acc;
        }, {});

        setScores(scoresMap);
        setLoading(false);

        // Calculate status counts for the pie chart
        const counts = scoreResults.reduce((acc, curr) => {
          const status = curr.scoreData.status || 'Error';
          acc[status] = (acc[status] || 0) + 1;
          return acc;
        }, {});
        setStatusCounts(counts);

      } catch (err) {
        console.error("Error fetching collaboration data:", err);
        setError("Failed to fetch collaboration data from the backend API.");
        setLoading(false);
      }
    };

    fetchTeamData();
  }, []); 

  if (loading) return <h2>Loading Collaboration Scores...</h2>;
  if (error) return <h2 style={{color: 'red'}}>{error}</h2>;

  // Simple styles
  const tableHeaderStyle = { border: '1px solid #ddd', padding: '12px', textAlign: 'left', backgroundColor: '#e9ecef' };
  const tableCellStyle = { border: '1px solid #ddd', padding: '8px' };

  return (
    <div style={{ fontFamily: 'Arial' }}>
      <h2>🤝 Team Collaboration Score</h2>
      <p>Classification based on sentiment and response ratio from chat data.</p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px', marginTop: '20px' }}>

        {/* Left Side: Pie Chart Visualization */}
        <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
            <h3>Team Collaboration Distribution</h3>
            <CollaborationPie statusCounts={statusCounts} />
        </div>

        {/* Right Side: Full Team Score Table */}
        <div style={{ overflowX: 'auto' }}>
            <h3>Developer Collaboration Status</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9em' }}>
                <thead>
                    <tr>
                        <th style={tableHeaderStyle}>Developer Name</th>
                        <th style={tableHeaderStyle}>Collaboration Score</th>
                        <th style={tableHeaderStyle}>Status</th>
                        <th style={tableHeaderStyle}>Features (Raw Data)</th>
                    </tr>
                </thead>
                <tbody>
                    {developers.map(dev => {
                        const scoreData = scores[dev.id] || {};
                        const score = scoreData.score || 'N/A';

                        const statusColor = scoreData.status === 'High' ? 'green' : scoreData.status === 'Medium' ? 'orange' : 'red';
                        const features = scoreData.features || {};

                        return (
                            <tr key={dev.id}>
                                <td style={tableCellStyle}>{dev.name}</td>
                                <td style={tableCellStyle}>{score}%</td>
                                <td style={{ ...tableCellStyle, color: statusColor, fontWeight: 'bold' }}>{scoreData.status}</td>
                                <td style={tableCellStyle}>
                                    Sentiment: {features.avg_sentiment ? features.avg_sentiment.toFixed(2) : 'N/A'} | Ratio: {features.response_ratio ? features.response_ratio.toFixed(2) : 'N/A'}
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>

      </div>
    </div>
  );
};

export default CollaborationPage;
