import { User, Event, EventDetail, Registration, Participant, AuditLog, SystemStats } from '../types';

const API_BASE = '/api';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    credentials: 'include', // Automatically passes and receives HttpOnly cookies
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const data = await response.json();
      if (data && data.detail) {
        errorMsg = data.detail;
      }
    } catch {
      // Non-JSON response
    }
    throw new Error(errorMsg);
  }

  // Handle 204 or empty responses
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const api = {
  // Authentication
  auth: {
    login: (email: string, password: string) =>
      request<{ access_token: string; user: User }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),
    logout: () =>
      request<{ message: string }>('/auth/logout', {
        method: 'POST',
      }),
    me: () => request<User>('/auth/me'),
  },

  // Events
  events: {
    list: (params?: { search?: string; category?: string; status?: string }) => {
      const searchParams = new URLSearchParams();
      if (params?.search) searchParams.append('search', params.search);
      if (params?.category) searchParams.append('category', params.category);
      if (params?.status) searchParams.append('status', params.status);
      const query = searchParams.toString();
      return request<Event[]>(`/events${query ? `?${query}` : ''}`);
    },
    get: (id: number) => request<EventDetail>(`/events/${id}`),
    create: (data: {
      title: string;
      description: string;
      category: string;
      venue: string;
      event_date: string;
      start_time: string;
      end_time: string;
      participant_limit: number;
      registration_deadline: string;
    }) =>
      request<Event>('/events', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: number, data: Partial<Event>) =>
      request<Event>(`/events/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    close: (id: number) =>
      request<Event>(`/events/${id}/close`, {
        method: 'POST',
      }),
  },

  // Registrations
  registrations: {
    register: (eventId: number) =>
      request<{ message: string; registration: Registration }>(`/events/${eventId}/register`, {
        method: 'POST',
      }),
    cancel: (registrationId: number) =>
      request<{ message: string }>(`/registrations/${registrationId}`, {
        method: 'DELETE',
      }),
    myRegistrations: () => request<Registration[]>('/registrations/me'),
    participants: (eventId: number) => request<Participant[]>(`/events/${eventId}/participants`),
  },

  // Admin
  admin: {
    users: () => request<User[]>('/admin/users'),
    updateRole: (userId: number, role: string) =>
      request<User>(`/admin/users/${userId}/role`, {
        method: 'PUT',
        body: JSON.stringify({ role }),
      }),
    events: () => request<Event[]>('/admin/events'),
    stats: () => request<SystemStats>('/admin/stats'),
    auditLogs: (limit = 100) => request<AuditLog[]>(`/admin/audit-logs?limit=${limit}`),
  },
};
