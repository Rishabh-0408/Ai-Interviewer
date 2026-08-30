/**
 * TypeScript types for job descriptions.
 */

export interface JobDescription {
  id: string;
  user_id: string;
  company: string;
  role: string;
  description_text: string;
  experience_level: string | null;
  url: string | null;
  created_at: string;
  updated_at: string;
}

export interface JobDescriptionCreate {
  company: string;
  role: string;
  description_text: string;
  experience_level?: string;
  url?: string;
}
