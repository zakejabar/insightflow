const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ResearchResponse {
  job_id: string;
  status: string;
}

export interface StatusResponse {
  job_id?: string;
  status: string;
  progress?: string;
  result?: {
    query: string;
    report: string;
    sources: Array<{
      title: string;
      url: string;
      content: string;
    }>;
    current_step?: string;
    insights: string[];
  };
  error?: string;
  logs?: string[];
  current_step?: string;
}

export async function startResearch(
  query: string,
  search_mode: string = "web",
  min_citations: number = 0,
  open_access: boolean = false
): Promise<ResearchResponse> {
  const response = await fetch(`${API_URL}/api/research`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, search_mode, min_citations, open_access }),
  });

  if (!response.ok) {
    throw new Error('Failed to start research');
  }

  return response.json();
}

export async function getStatus(jobId: string): Promise<StatusResponse> {
  const response = await fetch(`${API_URL}/api/status/${jobId}`);

  if (!response.ok) {
    throw new Error('Failed to get status');
  }

  return response.json();
}

export async function checkHealth() {
  const response = await fetch(`${API_URL}/api/health`);
  return response.json();
}