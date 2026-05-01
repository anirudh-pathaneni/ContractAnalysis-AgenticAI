import React from 'react';
import { AnalysisResponse } from '../api';

interface RiskDashboardProps {
  data: AnalysisResponse | null;
}

export const RiskDashboard: React.FC<RiskDashboardProps> = ({ data }) => {
  if (!data) return (
    <div className="glass-panel" style={{ padding: '24px', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
      Upload a contract to view risks and remediations.
    </div>
  );

  return (
    <div className="glass-panel animate-fade-in" style={{ padding: '24px', height: '100%', overflowY: 'auto' }}>
      <h2 style={{ margin: '0 0 24px 0', fontSize: '20px' }}>Risk Analysis</h2>
      
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ color: 'var(--text-secondary)', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px' }}>Identified Risks</h3>
        {data.risks && data.risks.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
            {data.risks.map((risk, i) => (
              <div key={i} style={{ padding: '16px', borderRadius: '8px', background: 'var(--bg-secondary)', borderLeft: `4px solid ${risk.risk_level.toLowerCase() === 'critical' ? 'var(--danger)' : risk.risk_level.toLowerCase() === 'high' ? 'var(--warning)' : 'var(--accent-color)'}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <strong style={{ fontSize: '14px' }}>{risk.risk_dimension}</strong>
                  <span style={{ fontSize: '12px', padding: '2px 8px', borderRadius: '12px', background: 'rgba(255,255,255,0.1)' }}>{risk.risk_level}</span>
                </div>
                <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{risk.reason}</p>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ fontSize: '14px', color: 'var(--success)' }}>No major risks identified.</p>
        )}
      </div>

      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ color: 'var(--text-secondary)', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px' }}>Remediation Suggestions</h3>
        {data.remediations && data.remediations.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
            {data.remediations.map((rem, i) => (
              <div key={i} style={{ padding: '16px', borderRadius: '8px', background: 'var(--bg-secondary)' }}>
                <strong style={{ fontSize: '14px', display: 'block', marginBottom: '8px', color: 'var(--accent-color)' }}>{rem.issue}</strong>
                <p style={{ margin: '0 0 8px 0', fontSize: '13px', lineHeight: 1.5 }}>{rem.suggestion}</p>
                <p style={{ margin: 0, fontSize: '12px', color: 'var(--text-secondary)', fontStyle: 'italic' }}>Justification: {rem.justification}</p>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>No remediations generated.</p>
        )}
      </div>

      <div>
        <h3 style={{ color: 'var(--text-secondary)', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px' }}>Assumptions & Uncertainties</h3>
        <ul style={{ paddingLeft: '20px', fontSize: '13px', lineHeight: 1.6, marginTop: '16px' }}>
          {data.assumptions?.map((ass, i) => <li key={`a-${i}`}>{ass}</li>)}
          {data.uncertainties?.map((unc, i) => <li key={`u-${i}`} style={{ color: 'var(--warning)' }}>{unc}</li>)}
        </ul>
      </div>
    </div>
  );
};
