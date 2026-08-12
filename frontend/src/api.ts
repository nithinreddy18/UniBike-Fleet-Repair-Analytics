const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_URL = baseUrl.endsWith('/api') ? baseUrl : `${baseUrl}/api`;

export const login = async (username: string, password: string) => {
  const response = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }
  return response.json();
};

export interface TicketPayload {
  bike_id: number;
  issue_type: string;
  description?: string;
}

export const submitTicket = async (payload: TicketPayload) => {
  const response = await fetch(`${API_URL}/tickets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to submit ticket');
  }
  return response.json();
};

export const chatAssistant = async (message: string) => {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to communicate with assistant');
  }
  return response.json();
};

export const fetchKpi = async () => {
  const response = await fetch(`${API_URL}/kpi`);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch KPIs');
  }
  return response.json();
};

export const fetchTickets = async () => {
  const response = await fetch(`${API_URL}/tickets`);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch tickets');
  }
  return response.json();
};

export const updateTicketStatus = async (ticketId: number, status: string) => {
  const response = await fetch(`${API_URL}/tickets/${ticketId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update ticket');
  }
  return response.json();
};
