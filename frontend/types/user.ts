/**
 * TypeScript types for user and candidate profile.
 */

export interface UserResponse {
  id: string;
  firebase_uid: string;
  email: string;
  display_name: string | null;
  photo_url: string | null;
  is_active: boolean;
  created_at: string;
}

export interface CandidateProfile {
  id: string;
  user_id: string;
  experience_level: string | null;
  target_role: string | null;
  target_company: string | null;
  bio: string | null;
  years_of_experience: number | null;
  current_role: string | null;
  current_company: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserWithProfile extends UserResponse {
  candidate_profile: CandidateProfile | null;
}

export interface CandidateProfileUpdate {
  experience_level?: string;
  target_role?: string;
  target_company?: string;
  bio?: string;
  years_of_experience?: number;
  current_role?: string;
  current_company?: string;
}
