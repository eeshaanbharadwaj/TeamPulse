// frontend/src/components/BurnoutGauge.js
import React from 'react';
import { RadialBarChart, RadialBar, Legend, ResponsiveContainer } from 'recharts';

const BurnoutGauge = ({ developerName, riskScore }) => {
  // Data structure required by Recharts RadialBarChart
  const data = [
    { 
      name: developerName, 
      uv: riskScore, // Score as a value out of 100
      fill: riskScore >= 50 ? '#ff4d4f' : '#52c41a' // Red for High Risk (>=50), Green for Low Risk
    },
  ];

  return (
    <div style={{ width: '100%', height: 200 }}>
      <ResponsiveContainer>
        <RadialBarChart 
          cx="50%" 
          cy="50%" 
          innerRadius="50%" 
          outerRadius="90%" 
          barSize={20} 
          data={data}
          startAngle={90} // Start from the top
          endAngle={450} // Full circle
        >
          <RadialBar 
            minAngle={15} 
            label={{ position: 'insideStart', fill: '#fff' }} 
            background 
            clockWise 
            dataKey="uv" 
          />
          <Legend 
            iconSize={10} 
            layout="vertical" 
            verticalAlign="middle" 
            wrapperStyle={{ 
              left: 300, top: 80 
            }}
          />

          {/* Custom Text Label in the center */}
          <text 
            x="50%" 
            y="50%" 
            dominantBaseline="middle" 
            textAnchor="middle" 
            fontSize="32" 
            fontWeight="bold"
            fill={data[0].fill}
          >
            {`${riskScore}%`}
          </text>

          <text 
            x="50%" 
            y="65%" 
            dominantBaseline="middle" 
            textAnchor="middle" 
            fontSize="14" 
            fill="#333"
          >
            Burnout Risk Score
          </text>
        </RadialBarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default BurnoutGauge;

