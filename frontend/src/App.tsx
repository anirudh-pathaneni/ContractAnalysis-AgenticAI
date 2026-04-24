import React from 'react';
import ReactFlow, { Background, Controls } from 'reactflow';
import 'reactflow/dist/style.css';

const initialNodes = [
  { id: '1', position: { x: 0, y: 0 }, data: { label: 'Contract Node' } },
  { id: '2', position: { x: 0, y: 100 }, data: { label: 'Clause 1' } },
];
const initialEdges = [{ id: 'e1-2', source: '1', target: '2' }];

function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '1rem', background: '#333', color: 'white' }}>
        <h1>Contract Intelligence Graph</h1>
      </header>
      <main style={{ flex: 1 }}>
        <ReactFlow nodes={initialNodes} edges={initialEdges}>
          <Background />
          <Controls />
        </ReactFlow>
      </main>
    </div>
  );
}

export default App;
