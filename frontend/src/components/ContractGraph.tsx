import React, { useMemo } from 'react';
import ReactFlow, { Background, Controls, Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';
import { AnalysisResponse } from '../api';

interface ContractGraphProps {
  data: AnalysisResponse | null;
}

export const ContractGraph: React.FC<ContractGraphProps> = ({ data }) => {
  const { nodes, edges } = useMemo(() => {
    if (!data) return { nodes: [], edges: [] };
    
    const initialNodes: Node[] = [
      {
        id: 'contract-root',
        position: { x: 250, y: 50 },
        data: { label: 'Contract Document' },
        style: { background: 'var(--accent-color)', color: 'white', border: 'none', borderRadius: '8px', padding: '10px 20px', fontWeight: 'bold' }
      }
    ];
    const initialEdges: Edge[] = [];

    // Map risks to clause ids to highlight nodes
    const risksMap: Record<string, string> = {};
    data.risks?.forEach(r => {
      risksMap[r.clause_id] = r.risk_level;
    });
    
    data.clauses?.forEach((clause, index) => {
        const cid = clause.clause_id;
        const riskLvl = risksMap[cid] || 'none';
        const isCritical = riskLvl.toLowerCase() === 'critical';
        const isHigh = riskLvl.toLowerCase() === 'high';
        
        let borderColor = 'var(--border-color)';
        if (isCritical) borderColor = 'var(--danger)';
        else if (isHigh) borderColor = 'var(--warning)';
        
        initialNodes.push({
            id: cid,
            position: { x: 50 + ((index%3) * 200), y: 150 + (Math.floor(index/3)*100) },
            data: { label: clause.heading },
            style: { 
                background: 'var(--bg-secondary)', 
                color: (isCritical || isHigh) ? borderColor : 'var(--text-primary)',
                border: `2px solid ${borderColor}`,
                borderRadius: '8px',
                width: 150
            }
        });
        
        initialEdges.push({
            id: `root-${cid}`,
            source: 'contract-root',
            target: cid,
            animated: isCritical || isHigh,
            style: { stroke: borderColor }
        });
    });

    return { nodes: initialNodes, edges: initialEdges };
  }, [data]);

  if (!data) {
    return (
      <div className="glass-panel" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Graph will visualize contract structure here.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel animate-fade-in" style={{ height: '100%', position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}>
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background color="var(--border-color)" gap={16} />
          <Controls style={{ background: 'var(--bg-secondary)', border: 'none', fill: 'var(--text-primary)' }} />
        </ReactFlow>
      </div>
    </div>
  );
};
