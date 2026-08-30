"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/navbar";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api";
import { 
  Briefcase, 
  Building2, 
  Clock, 
  Target, 
  Sparkles, 
  FileText, 
  CheckCircle2, 
  Layers, 
  ArrowRight,
  ShieldAlert,
  Loader2
} from "lucide-react";

interface ResumeItem {
  id: string;
  filename: string;
}

interface JobItem {
  id: string;
  title: string;
  company?: string;
}

const QUESTION_CATEGORIES = [
  { id: "technical", label: "Technical & Code", desc: "Architecture, data structures, domain knowledge" },
  { id: "behavioral", label: "Behavioral (STAR)", desc: "Past experiences, teamwork, conflict, impact" },
  { id: "case_study", label: "Case Study & System Design", desc: "Open-ended real-world problem scenarios" },
  { id: "analytical", label: "Analytical & Logic", desc: "Quantitative breakdown, metrics, problem-solving" },
  { id: "situational", label: "Situational / Hypothetical", desc: "Critical thinking under pressure & ambiguity" },
  { id: "leadership_teamwork", label: "Leadership & Culture", desc: "Mentorship, vision, cross-functional impact" },
  { id: "personal_motivational", label: "Motivation & Goals", desc: "Role alignment, values, career trajectory" },
  { id: "rapid_fire_icebreaker", label: "Rapid Fire & Intro", desc: "Fast-paced warm-up questions" },
];

export default function InterviewSetupPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const [mode, setMode] = useState<"practice" | "simulation">("practice");
  const [role, setRole] = useState("");
  const [company, setCompany] = useState("");
  const [experienceLevel, setExperienceLevel] = useState("mid");
  const [durationMinutes, setDurationMinutes] = useState(20);
  const [selectedCategories, setSelectedCategories] = useState<string[]>(["technical", "behavioral"]);
  
  const [resumes, setResumes] = useState<ResumeItem[]>([]);
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<string>("");
  const [selectedJobId, setSelectedJobId] = useState<string>("");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
      return;
    }

    if (user) {
      // Fetch user's existing resumes and jobs
      api.get<ResumeItem[]>("/api/v1/resumes")
        .then((data) => {
          if (Array.isArray(data)) {
            setResumes(data);
            if (data.length > 0) setSelectedResumeId(data[0].id);
          }
        })
        .catch(() => {});

      api.get<JobItem[]>("/api/v1/jobs")
        .then((data) => {
          if (Array.isArray(data)) {
            setJobs(data);
            if (data.length > 0) setSelectedJobId(data[0].id);
          }
        })
        .catch(() => {});
    }
  }, [user, authLoading, router]);

  const toggleCategory = (id: string) => {
    if (selectedCategories.includes(id)) {
      if (selectedCategories.length > 1) {
        setSelectedCategories(selectedCategories.filter((c) => c !== id));
      }
    } else {
      setSelectedCategories([...selectedCategories, id]);
    }
  };

  const handleLaunch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!role.trim()) {
      setError("Please specify the target role.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const payload = {
        mode,
        role: role.trim(),
        company: company.trim() || undefined,
        experience_level: experienceLevel,
        duration_minutes: Number(durationMinutes),
        resume_id: selectedResumeId || undefined,
        job_description_id: selectedJobId || undefined,
        selected_question_types: mode === "practice" ? selectedCategories : undefined,
      };

      const interview = await api.post<{ id: string }>("/api/v1/interviews", payload);
      router.push(`/interview/${interview.id}`);
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : "Failed to launch interview session";
      setError(errorMsg);
      setIsSubmitting(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#0d0e1a] text-white flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0d0e1a] text-white flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-indigo-400 via-purple-300 to-pink-400 bg-clip-text text-transparent">
            Setup Your AI Interview
          </h1>
          <p className="text-gray-400 mt-2 text-sm sm:text-base">
            Customize your session. Our AI researches role expectations and adapts questions in real-time.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-3 text-red-400 text-sm">
            <ShieldAlert className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLaunch} className="space-y-8">
          {/* Mode Selector */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div
              onClick={() => setMode("practice")}
              className={`cursor-pointer p-5 rounded-2xl border transition-all ${
                mode === "practice"
                  ? "bg-indigo-600/15 border-indigo-500 shadow-[0_0_25px_rgba(99,102,241,0.2)]"
                  : "bg-white/[0.03] border-white/10 hover:border-white/20"
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center text-indigo-400">
                  <Target className="w-5 h-5" />
                </div>
                {mode === "practice" && <CheckCircle2 className="w-5 h-5 text-indigo-400" />}
              </div>
              <h3 className="font-semibold text-lg">Focused Practice Mode</h3>
              <p className="text-gray-400 text-xs mt-1">
                Handpick specific question categories to target. Adaptive turns within your chosen competencies.
              </p>
            </div>

            <div
              onClick={() => setMode("simulation")}
              className={`cursor-pointer p-5 rounded-2xl border transition-all ${
                mode === "simulation"
                  ? "bg-purple-600/15 border-purple-500 shadow-[0_0_25px_rgba(168,85,247,0.2)]"
                  : "bg-white/[0.03] border-white/10 hover:border-white/20"
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center text-purple-400">
                  <Sparkles className="w-5 h-5" />
                </div>
                {mode === "simulation" && <CheckCircle2 className="w-5 h-5 text-purple-400" />}
              </div>
              <h3 className="font-semibold text-lg">Real Interview Simulation</h3>
              <p className="text-gray-400 text-xs mt-1">
                AI dynamically orchestrates the full interview structure (Intro, Technical, System Design, Behavioral, Closing).
              </p>
            </div>
          </div>

          {/* Role and Company */}
          <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10 space-y-5">
            <h3 className="font-medium text-sm text-indigo-300 uppercase tracking-wider flex items-center gap-2">
              <Briefcase className="w-4 h-4" /> Role & Context
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-300 mb-1.5">Target Role *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Senior Backend Engineer"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 focus:border-indigo-500 focus:outline-none text-sm placeholder-gray-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-300 mb-1.5">Target Company (Optional)</label>
                <div className="relative">
                  <input
                    type="text"
                    placeholder="e.g. Google, Stripe, or Startup"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 focus:border-indigo-500 focus:outline-none text-sm placeholder-gray-500 transition-colors"
                  />
                  <Building2 className="w-4 h-4 text-gray-500 absolute right-3 top-3 pointer-events-none" />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div>
                <label className="block text-xs font-medium text-gray-300 mb-1.5">Experience Level</label>
                <select
                  value={experienceLevel}
                  onChange={(e) => setExperienceLevel(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#171828] border border-white/10 focus:border-indigo-500 focus:outline-none text-sm text-gray-200"
                >
                  <option value="junior">Junior / Entry Level (0-2 yrs)</option>
                  <option value="mid">Mid-Level (3-5 yrs)</option>
                  <option value="senior">Senior (6-9 yrs)</option>
                  <option value="staff">Staff / Principal / Lead (10+ yrs)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-300 mb-1.5 flex items-center justify-between">
                  <span>Duration</span>
                  <span className="text-indigo-400 font-semibold">{durationMinutes} Minutes</span>
                </label>
                <div className="flex items-center gap-3">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <input
                    type="range"
                    min="10"
                    max="60"
                    step="5"
                    value={durationMinutes}
                    onChange={(e) => setDurationMinutes(Number(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Practice Categories (Only visible in Practice mode) */}
          {mode === "practice" && (
            <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10 space-y-4">
              <h3 className="font-medium text-sm text-indigo-300 uppercase tracking-wider flex items-center gap-2">
                <Layers className="w-4 h-4" /> Focus Categories
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {QUESTION_CATEGORIES.map((cat) => {
                  const isSelected = selectedCategories.includes(cat.id);
                  return (
                    <div
                      key={cat.id}
                      onClick={() => toggleCategory(cat.id)}
                      className={`p-3.5 rounded-xl border cursor-pointer transition-all flex items-start gap-3 ${
                        isSelected
                          ? "bg-indigo-600/10 border-indigo-500/60"
                          : "bg-white/[0.02] border-white/5 hover:border-white/15"
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => {}}
                        className="mt-1 accent-indigo-500 rounded"
                      />
                      <div>
                        <div className="text-sm font-medium text-gray-200">{cat.label}</div>
                        <div className="text-xs text-gray-400 mt-0.5">{cat.desc}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Context Links (Resume & Job Description) */}
          <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10 space-y-4">
            <h3 className="font-medium text-sm text-indigo-300 uppercase tracking-wider flex items-center gap-2">
              <FileText className="w-4 h-4" /> Evidence Context
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-300 mb-1.5">Linked Resume</label>
                <select
                  value={selectedResumeId}
                  onChange={(e) => setSelectedResumeId(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#171828] border border-white/10 focus:border-indigo-500 focus:outline-none text-sm text-gray-200"
                >
                  <option value="">No resume attached</option>
                  {resumes.map((r) => (
                    <option key={r.id} value={r.id}>{r.filename}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-300 mb-1.5">Linked Job Description</label>
                <select
                  value={selectedJobId}
                  onChange={(e) => setSelectedJobId(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#171828] border border-white/10 focus:border-indigo-500 focus:outline-none text-sm text-gray-200"
                >
                  <option value="">No specific JD attached</option>
                  {jobs.map((j) => (
                    <option key={j.id} value={j.id}>{j.title} {j.company ? `(${j.company})` : ""}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Launch Action */}
          <div className="flex justify-end pt-4">
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-medium flex items-center gap-2 shadow-[0_0_30px_rgba(99,102,241,0.3)] transition-all disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Preparing AI Interviewer...</span>
                </>
              ) : (
                <>
                  <span>Begin Interview Session</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
