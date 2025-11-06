// frontend/src/components/ProductivityBar.js
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const ProductivityBar = ({ developerName, score }) => {
  const data = [
    { 
      name: developerName, 
      score: score,
      max: 100,
      // Color changes based on score: High (>80) is blue, Medium (>50) is orange
      fill: score >= 80 ? '#1890ff' : score >= 50 ? '#faad14' : '#f5222d' 
    },
  ];

  return (
    <div style={{ height: 60, width: '100%', marginBottom: '20px' }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart layout="vertical" data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <XAxis type="number" hide domain={[0, 100]} />
          <YAxis type="category" dataKey="name" width={100} />
          <Tooltip />
          <Bar 
            dataKey="score" 
            fill={data[0].fill} 
            background={{ fill: '#eee' }} 
            radius={[5, 5, 5, 5]} // Rounded edges
          />
          <text 
            x="90%" 
            y="50%" 
            dominantBaseline="middle" 
            textAnchor="end" 
            fontSize="18" 
            fontWeight="bold"
            fill="#333"
          >
            {`${score.toFixed(0)}%`}
          </text>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ProductivityBar;

