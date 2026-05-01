export interface AnalysisResponse {
  contract_id: string;
  status: string;
  clauses: Array<{
    clause_id: string;
    heading: string;
    raw_text: string;
  }>;
  risks: Array<{
    clause_id: string;
    risk_dimension: string;
    risk_level: string;
    reason: string;
  }>;
  remediations: Array<{
    issue: string;
    suggestion: string;
    justification: string;
  }>;
  assumptions: string[];
  uncertainties: string[];
}

export const analyzeContract = async (
  file: File,
  userRole: string,
  counterpartyRole: string,
  contractType: string,
  jurisdiction: string
): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('user_role', userRole);
  formData.append('counterparty_role', counterpartyRole);
  formData.append('contract_type', contractType);
  formData.append('jurisdiction', jurisdiction);

  const response = await fetch('http://localhost:8080/analyze-file', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorDetail = 'Failed to analyze contract';
    try {
      const errorData = await response.json();
      if (errorData.detail) errorDetail = errorData.detail;
    } catch(e) {}
    throw new Error(errorDetail);
  }

  return await response.json();
};
