/**
 * TypeScript types for resumes.
 */

export interface ResumeResponse {
  id: string;
  filename: string;
  content_type: string;
  file_size: number;
  is_primary: boolean;
  created_at: string;
}

export interface ResumeListResponse {
  resumes: ResumeResponse[];
  total: number;
}
