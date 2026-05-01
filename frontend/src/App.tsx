import React, { useState } from 'react';
import { UploadForm } from './components/UploadForm';
import { RiskDashboard } from './components/RiskDashboard';
import { ContractGraph } from './components/ContractGraph';
import { AnalysisResponse } from './api';

function App() {
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '20px 32px', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-color)' }}>
        <h1 className="gradient-text" style={{ margin: 0, fontSize: '24px' }}>Nexus AI: Contract Intelligence</h1>
      </header>

      <main style={{ flex: 1, padding: '24px', display: 'grid', gridTemplateColumns: '350px 1fr 400px', gap: '24px', overflow: 'hidden' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto' }}>
          <UploadForm 
            onAnalysisStart={() => { setError(null); setAnalysisData(null); }}
            onAnalysisComplete={(data) => setAnalysisData(data)}
            onError={(err) => setError(err)}
          />
          
          {error && (
            <div className="animate-fade-in glass-panel" style={{ padding: '16px', background: 'rgba(255, 71, 87, 0.1)', border: '1px solid var(--danger)', color: 'var(--danger)', fontSize: '14px' }}>
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>

        <div style={{ height: '100%', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <ContractGraph data={analysisData} />
        </div>

        <div style={{ height: '100%', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <RiskDashboard data={analysisData} />
        </div>
      </main>
    </div>
  );
}

export default App;
