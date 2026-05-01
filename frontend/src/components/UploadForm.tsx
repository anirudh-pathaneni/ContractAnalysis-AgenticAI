import React, { useState } from 'react';
import { analyzeContract } from '../api';

interface UploadFormProps {
  onAnalysisStart: () => void;
  onAnalysisComplete: (data: any) => void;
  onError: (err: string) => void;
}

export const UploadForm: React.FC<UploadFormProps> = ({ onAnalysisStart, onAnalysisComplete, onError }) => {
  const [file, setFile] = useState<File | null>(null);
  const [userRole, setUserRole] = useState('Employer');
  const [counterpartyRole, setCounterpartyRole] = useState('Employee');
  const [contractType, setContractType] = useState('Employment');
  const [jurisdiction, setJurisdiction] = useState('India');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      onError("Please select a file to analyze.");
      return;
    }

    setIsLoading(true);
    onAnalysisStart();
    try {
      const data = await analyzeContract(file, userRole, counterpartyRole, contractType, jurisdiction);
      onAnalysisComplete(data);
    } catch (err: any) {
      onError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="glass-panel animate-fade-in" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <h2 style={{ margin: '0 0 16px 0', fontSize: '18px' }}>Context Intake</h2>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Upload Document (PDF/DOCX)</label>
        <div style={{ border: '2px dashed var(--border-color)', padding: '20px', borderRadius: '8px', textAlign: 'center', cursor: 'pointer' }}>
          <input type="file" accept=".pdf,.doc,.docx,.txt" onChange={(e) => setFile(e.target.files?.[0] || null)} style={{ width: '100%' }} />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Your Role</label>
          <input value={userRole} onChange={(e) => setUserRole(e.target.value)} />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Counterparty Role</label>
          <input value={counterpartyRole} onChange={(e) => setCounterpartyRole(e.target.value)} />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Contract Type</label>
          <input value={contractType} onChange={(e) => setContractType(e.target.value)} />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Jurisdiction</label>
          <input value={jurisdiction} onChange={(e) => setJurisdiction(e.target.value)} />
        </div>
      </div>

      <button type="submit" disabled={isLoading} style={{ marginTop: '16px' }}>
        {isLoading ? 'Analyzing via Agentic AI...' : 'Analyze Contract'}
      </button>
    </form>
  );
};
