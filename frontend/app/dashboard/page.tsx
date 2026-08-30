"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { Navbar } from "@/components/layout/navbar";
import { PageLoading } from "@/components/ui/loading";
import { api } from "@/lib/api";
import {
  Target,
  Sparkles,
  ArrowRight,
  Clock,
  Award,
  Upload,
  FileText,
  Briefcase,
  CheckCircle2,
  TrendingUp,
} from "lucide-react";

interface InterviewSummary {
  id: string;
  role?: string;
  company?: string;
  mode: string;
  status: string;
  duration_minutes?: number;
  overall_score?: number;
  created_at: string;
  completed_at?: string;
}

export default function DashboardPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  const [interviews, setInterviews] = useState<InterviewSummary[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (user) {
      api.get<InterviewSummary[]>("/api/v1/interviews")
        .then((data) => {
          if (Array.isArray(data)) {
            setInterviews(data);
          }
          setLoadingHistory(false);
        })
        .catch(() => {
          setLoadingHistory(false);
        });
    }
  }, [user]);

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingResume(true);
    setUploadSuccess(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.upload("/api/v1/resumes/upload", formData);
      setUploadSuccess(`Uploaded ${file.name} successfully!`);
    } catch {
      setUploadSuccess("Upload failed. Please ensure the file is a PDF or text format.");
    } finally {
      setUploadingResume(false);
    }
  };

  if (loading || !user) {
    return <PageLoading />;
  }

  const completedCount = interviews.filter((i) => i.status === "completed").length;
  const avgScore =
    completedCount > 0
      ? Math.round(
          interviews
            .filter((i) => i.overall_score !== null && i.overall_score !== undefined)
            .reduce((acc, curr) => acc + (curr.overall_score || 0), 0) /
            Math.max(completedCount, 1)
        )
      : 0;

  return (
    <>
      <Navbar />

      <main className="flex-1 relative min-h-screen pb-16">
        {/* Background accents */}
        <div
          className="glow-orb glow-orb-primary"
          style={{ width: 350, height: 350, top: "5%", right: "10%" }}
        />
        <div
          className="glow-orb glow-orb-secondary"
          style={{ width: 300, height: 300, bottom: "15%", left: "5%" }}
        />

        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-10 relative">
          {/* Welcome & Quick Action */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-10">
            <div>
              <h1 className="font-[var(--font-outfit)] text-3xl sm:text-4xl font-bold mb-1.5 bg-gradient-to-r from-white via-gray-200 to-indigo-300 bg-clip-text text-transparent">
                Welcome back{user.displayName ? `, ${user.displayName}` : ""}
              </h1>
              <p className="text-gray-400 text-sm sm:text-base">
                Evidence-driven interview simulation tailored to your background.
              </p>
            </div>

            <Link
              href="/interview/setup"
              className="px-6 py-3 rounded-2xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-medium text-sm flex items-center gap-2 shadow-[0_0_25px_rgba(99,102,241,0.3)] transition-all shrink-0"
            >
              <Sparkles className="w-4 h-4" />
              <span>Launch New Interview</span>
            </Link>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/10 text-center">
              <div className="text-xl mb-1">📋</div>
              <div className="font-[var(--font-outfit)] text-2xl font-bold text-white">
                {interviews.length}
              </div>
              <div className="text-xs text-gray-400">Total Sessions</div>
            </div>

            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/10 text-center">
              <div className="text-xl mb-1">✅</div>
              <div className="font-[var(--font-outfit)] text-2xl font-bold text-white">
                {completedCount}
              </div>
              <div className="text-xs text-gray-400">Completed</div>
            </div>

            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/10 text-center">
              <div className="text-xl mb-1">⭐</div>
              <div className="font-[var(--font-outfit)] text-2xl font-bold text-indigo-400">
                {avgScore > 0 ? `${avgScore}/100` : "—"}
              </div>
              <div className="text-xs text-gray-400">Average Readiness</div>
            </div>

            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/10 text-center">
              <div className="text-xl mb-1">⏱️</div>
              <div className="font-[var(--font-outfit)] text-2xl font-bold text-purple-400">
                {interviews.reduce((acc, i) => acc + (i.duration_minutes || 20), 0)}m
              </div>
              <div className="text-xs text-gray-400">Practice Time</div>
            </div>
          </div>

          {/* Mode Selection Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            {/* Focused Practice */}
            <div
              onClick={() => router.push("/interview/setup")}
              className="p-6 sm:p-8 rounded-3xl bg-gradient-to-b from-white/[0.04] to-white/[0.01] border border-white/10 hover:border-indigo-500/50 hover:shadow-[0_0_30px_rgba(99,102,241,0.2)] transition-all cursor-pointer group flex flex-col justify-between"
            >
              <div>
                <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Target className="w-6 h-6" />
                </div>
                <h2 className="font-[var(--font-outfit)] text-xl sm:text-2xl font-semibold mb-2 text-white">
                  Focused Practice
                </h2>
                <p className="text-gray-400 text-xs sm:text-sm leading-relaxed mb-4">
                  Select specific competencies (Technical, Behavioral STAR, System Design, Situational) and train with adaptive follow-up probing.
                </p>
                <div className="flex flex-wrap gap-1.5 mb-6">
                  {["Technical", "Behavioral", "System Design", "Leadership"].map((t) => (
                    <span
                      key={t}
                      className="text-[11px] px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-2 text-indigo-400 text-xs sm:text-sm font-semibold group-hover:translate-x-1 transition-transform">
                <span>Configure Practice</span>
                <ArrowRight className="w-4 h-4" />
              </div>
            </div>

            {/* Real Interview Simulation */}
            <div
              onClick={() => router.push("/interview/setup")}
              className="p-6 sm:p-8 rounded-3xl bg-gradient-to-b from-white/[0.04] to-white/[0.01] border border-white/10 hover:border-purple-500/50 hover:shadow-[0_0_30px_rgba(168,85,247,0.2)] transition-all cursor-pointer group flex flex-col justify-between"
            >
              <div>
                <div className="w-12 h-12 rounded-2xl bg-purple-500/20 text-purple-400 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Sparkles className="w-6 h-6" />
                </div>
                <h2 className="font-[var(--font-outfit)] text-xl sm:text-2xl font-semibold mb-2 text-white">
                  Full Interview Simulation
                </h2>
                <p className="text-gray-400 text-xs sm:text-sm leading-relaxed mb-4">
                  Experience a full-length, role-researched interview dynamically structured across icebreakers, deep technicals, and situational questions.
                </p>
                <div className="flex flex-wrap gap-1.5 mb-6">
                  {["Role Intelligence", "Dynamic Stage Plan", "Scorecard Report"].map((f) => (
                    <span
                      key={f}
                      className="text-[11px] px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20"
                    >
                      {f}
                    </span>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-2 text-purple-400 text-xs sm:text-sm font-semibold group-hover:translate-x-1 transition-transform">
                <span>Start Simulation</span>
                <ArrowRight className="w-4 h-4" />
              </div>
            </div>
          </div>

          {/* Resume Upload & Evidence Card */}
          <div className="p-6 rounded-3xl bg-white/[0.02] border border-white/10 mb-12 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-gray-300 shrink-0">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-semibold text-sm sm:text-base text-gray-200">Candidate Resume & Evidence</h3>
                <p className="text-xs text-gray-400 mt-0.5">
                  Upload your PDF resume so the AI can formulate personalized questions directly testing your experience.
                </p>
                {uploadSuccess && (
                  <p className="text-xs text-emerald-400 mt-1 font-medium">{uploadSuccess}</p>
                )}
              </div>
            </div>

            <label className="cursor-pointer px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs sm:text-sm font-medium text-gray-200 flex items-center gap-2 transition-colors shrink-0">
              <Upload className="w-4 h-4 text-indigo-400" />
              <span>{uploadingResume ? "Uploading & Extracting..." : "Upload Resume (PDF)"}</span>
              <input
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleResumeUpload}
                disabled={uploadingResume}
                className="hidden"
              />
            </label>
          </div>

          {/* Recent Interview History */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-[var(--font-outfit)] text-lg font-semibold text-gray-200 flex items-center gap-2">
                <Clock className="w-4 h-4 text-indigo-400" /> Your Interview Sessions
              </h3>
            </div>

            {loadingHistory ? (
              <div className="p-8 text-center text-xs text-gray-500">Loading your history...</div>
            ) : interviews.length === 0 ? (
              <div className="p-10 rounded-3xl bg-white/[0.01] border border-white/5 text-center flex flex-col items-center justify-center">
                <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-3">
                  <Briefcase className="w-6 h-6" />
                </div>
                <h4 className="font-medium text-sm text-gray-300">No interview sessions yet</h4>
                <p className="text-xs text-gray-500 mt-1 max-w-sm">
                  Launch your first practice session or simulation to get structured scoring and AI coaching.
                </p>
                <Link
                  href="/interview/setup"
                  className="mt-4 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-xs font-medium text-white transition-colors"
                >
                  Start First Session
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-3">
                {interviews.map((session) => (
                  <Link
                    key={session.id}
                    href={
                      session.status === "completed"
                        ? `/reports/${session.id}`
                        : `/interview/${session.id}`
                    }
                    className="p-4 rounded-2xl bg-white/[0.02] border border-white/10 hover:border-white/20 transition-all flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-9 h-9 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-indigo-400 shrink-0">
                        {session.status === "completed" ? (
                          <Award className="w-4 h-4 text-emerald-400" />
                        ) : (
                          <Clock className="w-4 h-4 text-indigo-400" />
                        )}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-sm text-gray-200">
                            {session.role || "General Interview"}
                          </span>
                          {session.company && (
                            <span className="text-[11px] px-2 py-0.5 rounded-full bg-white/10 text-gray-300">
                              {session.company}
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-gray-400 capitalize mt-0.5">
                          {session.mode} Mode • {session.duration_minutes || 20} min • {new Date(session.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      {session.overall_score !== null && session.overall_score !== undefined ? (
                        <div className="text-right">
                          <span className="text-sm font-bold text-emerald-400">
                            {Math.round(session.overall_score)}/100
                          </span>
                          <div className="text-[10px] text-gray-400">View Report</div>
                        </div>
                      ) : (
                        <span className="text-xs px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20">
                          In Progress
                        </span>
                      )}
                      <ArrowRight className="w-4 h-4 text-gray-500 group-hover:translate-x-1 group-hover:text-gray-300 transition-all" />
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  );
}
