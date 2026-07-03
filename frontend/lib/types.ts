export type LeadStatus = "PENDING" | "REACHED_OUT";

export interface Lead {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  resume_filename: string;
  status: LeadStatus;
  created_at: string;
  updated_at: string;
}
