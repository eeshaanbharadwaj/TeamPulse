// frontend/src/components/CollaborationPie.js
import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Define colors for the three collaboration classes
const COLORS = {
  'High': '#52c41a',   // Green
  'Medium': '#faad14', // Orange
  'Low': '#f5222d',    // Red
  'Error': '#aaa'
};

const CollaborationPie = ({ statusCounts }) => {
  // Data must be formatted as an array of objects for Recharts
  const pieData = [
    { name: 'High', value: statusCounts.High || 0 },
    { name: 'Medium', value: statusCounts.Medium || 0 },
    { name: 'Low', value: statusCounts.Low || 0 },
  ].filter(item => item.value > 0); // Filter out zero values for cleaner chart

  return (
    <div style={{ width: '100%', height: 300, margin: '20px 0' }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={pieData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={100}
            fill="#8884d8"
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          >
            {/* Assign colors based on the status name */}
            {pieData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => `${value} Devs`} />
          <Legend verticalAlign="bottom" height={36} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CollaborationPie;

