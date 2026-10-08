export type UserRole = 'STUDENT' | 'FACULTY' | 'ADMIN' | 'GUEST';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type EventStatus = 'OPEN' | 'CLOSED' | 'CANCELLED';

export interface Event {
  id: number;
  organizer_id: number;
  title: string;
  description: string;
  category: string;
  venue: string;
  event_date: string;
  start_time: string;
  end_time: string;
  participant_limit: number;
  registration_deadline: string;
  status: EventStatus;
  registered_count: number;
  available_seats: number;
  organizer_name?: string;
  created_at: string;
  updated_at: string;
}

export interface EventDetail extends Event {
  is_registered_by_user: boolean;
  user_registration_id?: number;
}

export type RegistrationStatus = 'CONFIRMED' | 'CANCELLED';

export interface Registration {
  id: number;
  event_id: number;
  student_id: number;
  registered_at: string;
  status: RegistrationStatus;
  cancelled_at?: string;
  event_title?: string;
  event_date?: string;
  venue?: string;
  category?: string;
}

export interface Participant {
  registration_id: number;
  student_id: number;
  student_name: string;
  student_email: string;
  registered_at: string;
  status: RegistrationStatus;
}

export interface AuditLog {
  id: number;
  actor_id?: number;
  actor_name?: string;
  actor_email?: string;
  action: string;
  entity_type: string;
  entity_id?: number;
  timestamp: string;
  source_ip?: string;
  result: string;
  metadata_json?: string;
}

export interface SystemStats {
  total_users: number;
  total_students: number;
  total_faculty: number;
  total_events: number;
  active_events: number;
  total_registrations: number;
  confirmed_registrations: number;
  total_audit_logs: number;
}
