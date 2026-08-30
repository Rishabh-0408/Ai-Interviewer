"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/navbar";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api";
import {
  Award,
  TrendingUp,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  RotateCcw,
  Target,
  Clock,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Loader2,
  FileText,
} from "lucide-react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

export default function InterviewReportPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const interviewId = resolvedParams.id;

  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [expandedTurns, setExpandedTurns] = useState<Record<number, boolean>>({});

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
      return;
    }

    if (user && interviewId) {
      setLoading(true);
      api.get<any>(`/api/v1/reports/${interviewId}`)
        .then((data) => {
          setReport(data);
          // Expand all turns by default
          const initialExpanded: Record<number, boolean> = {};
          (data.turns || []).forEach((_: any, idx: number) => {
            initialExpanded[idx] = true;
          });
          setExpandedTurns(initialExpanded);
          setLoading(false);
        })
        .catch((err) => {
          setError(err instanceof Error ? err.message : "Failed to load report");
          setLoading(false);
        });
    }
  }, [user, authLoading, interviewId, router]);

  const toggleTurn = (index: number) => {
    setExpandedTurns((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const getScoreBadge = (score: number) => {
    if (score >= 85) {
      return { label: "Strong Hire", color: "text-emerald-400 bg-emerald-500/15 border-emerald-500/30" };
    }
    if (score >= 70) {
      return { label: "Hire / Solid", color: "text-indigo-400 bg-indigo-500/15 border-indigo-500/30" };
    }
    if (score >= 55) {
      return { label: "Needs Polish", color: "text-amber-400 bg-amber-500/15 border-amber-500/30" };
    }
    return { label: "Needs Preparation", color: "text-red-400 bg-red-500/15 border-red-500/30" };
  };

  if (loading || authLoading) {
    return (
      <div className="min-h-screen bg-[#0d0e1a] text-white flex flex-col items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mb-3" />
        <p className="text-gray-400 text-sm">Compiling Performance Report & Insights...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="min-h-screen bg-[#0d0e1a] text-white flex flex-col">
        <Navbar />
        <div className="flex-1 flex flex-col items-center justify-center p-4">
          <p className="text-red-400 mb-4">{error || "Report not found"}</p>
          <Link href="/dashboard" className="px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 text-sm">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const scoreBadge = getScoreBadge(report.overall_score || 75);
  const chartData = report.competency_chart || [];

  return (
    <div className="min-h-screen bg-[#0d0e1a] text-white flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-8 space-y-8">
        {/* Header Summary */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 rounded-3xl bg-gradient-to-r from-indigo-950/40 via-purple-950/20 to-transparent border border-white/10">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl sm:text-3xl font-bold">{report.role || "Candidate Interview"}</h1>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${scoreBadge.color}`}>
                {scoreBadge.label}
              </span>
            </div>
            <p className="text-gray-400 text-xs sm:text-sm mt-1">
              {report.company ? `Simulated for ${report.company} • ` : ""}
              {report.mode ? `${report.mode.toUpperCase()} Mode • ` : ""}
              Completed {new Date(report.completed_at || Date.now()).toLocaleDateString()}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/interview/setup"
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 font-medium text-xs sm:text-sm flex items-center gap-2 transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Practice Again</span>
            </Link>
            <Link
              href="/dashboard"
              className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs sm:text-sm transition-colors"
            >
              Dashboard
            </Link>
          </div>
        </div>

        {/* Score & Analytics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Overall Score Card */}
          <div className="p-6 rounded-3xl bg-white/[0.02] border border-white/10 flex flex-col items-center justify-center text-center">
            <span className="text-xs uppercase tracking-wider font-semibold text-gray-400">Overall Readiness Score</span>
            <div className="relative my-4 flex items-center justify-center">
              <div className="w-32 h-32 rounded-full border-4 border-indigo-500/20 flex flex-col items-center justify-center">
                <span className="text-4xl font-extrabold text-transparent bg-gradient-to-r from-indigo-400 to-purple-300 bg-clip-text">
                  {Math.round(report.overall_score || 75)}
                </span>
                <span className="text-xs text-gray-500 font-medium">out of 100</span>
              </div>
            </div>
            <p className="text-xs text-gray-400">
              Evaluated across {report.turns?.length || 0} questions and follow-ups.
            </p>
          </div>

          {/* Radar / Competency Chart */}
          <div className="md:col-span-2 p-6 rounded-3xl bg-white/[0.02] border border-white/10 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs uppercase tracking-wider font-semibold text-indigo-300 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" /> Competency Breakdown
              </span>
            </div>

            <div className="h-56 w-full flex items-center justify-center">
              {chartData.length >= 3 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="75%" data={chartData}>
                    <PolarGrid stroke="rgba(255,255,255,0.1)" />
                    <PolarAngleAxis dataKey="competency" stroke="#9ca3af" tick={{ fill: "#9ca3af", fontSize: 11 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#4b5563" />
                    <Radar name="Score" dataKey="score" stroke="#818cf8" fill="#6366f1" fillOpacity={0.4} />
                  </RadarChart>
                </ResponsiveContainer>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <XAxis dataKey="competency" stroke="#9ca3af" fontSize={11} />
                    <YAxis domain={[0, 100]} stroke="#9ca3af" fontSize={11} />
                    <Tooltip contentStyle={{ backgroundColor: "#1e1f38", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px" }} />
                    <Bar dataKey="score" fill="#6366f1" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>

        {/* Turn-by-Turn Question Breakdown */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-gray-200 flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" /> Turn-by-Turn Question & Feedback Analysis
          </h2>

          {(report.turns || []).map((turn: any, index: number) => {
            const isExpanded = !!expandedTurns[index];
            return (
              <div
                key={index}
                className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 hover:border-white/15 transition-all"
              >
                <div
                  onClick={() => toggleTurn(index)}
                  className="flex items-center justify-between cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-7 h-7 rounded-lg bg-indigo-600/20 text-indigo-400 font-bold text-xs flex items-center justify-center">
                      Q{turn.order || index + 1}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm text-gray-200 line-clamp-1">
                          {turn.question_text}
                        </span>
                        {turn.is_followup && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30">
                            Follow-up
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-gray-400 capitalize mt-0.5">
                        {turn.question_type?.replace("_", " ")}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-sm font-bold text-indigo-400">{turn.score}/100</span>
                    {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
                  </div>
                </div>

                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-white/5 space-y-4 text-xs sm:text-sm">
                    {/* Candidate Answer */}
                    <div>
                      <div className="text-xs uppercase font-semibold text-gray-400 mb-1">Candidate Answer</div>
                      <p className="p-3 rounded-xl bg-white/5 text-gray-300 leading-relaxed italic">
                        &ldquo;{turn.answer_text || "No response recorded"}&rdquo;
                      </p>
                    </div>

                    {/* Evaluator Feedback */}
                    <div>
                      <div className="text-xs uppercase font-semibold text-emerald-400 mb-1">Evaluator Feedback</div>
                      <p className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-200 leading-relaxed">
                        {turn.feedback}
                      </p>
                    </div>

                    {/* Strengths and Gaps */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {turn.strengths && turn.strengths.length > 0 && (
                        <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                          <div className="font-semibold text-gray-300 flex items-center gap-1.5 mb-2 text-xs">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Key Strengths
                          </div>
                          <ul className="list-disc list-inside space-y-1 text-gray-400 text-xs">
                            {turn.strengths.map((s: string, i: number) => (
                              <li key={i}>{s}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {turn.weaknesses && turn.weaknesses.length > 0 && (
                        <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                          <div className="font-semibold text-gray-300 flex items-center gap-1.5 mb-2 text-xs">
                            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> Areas to Polish
                          </div>
                          <ul className="list-disc list-inside space-y-1 text-gray-400 text-xs">
                            {turn.weaknesses.map((w: string, i: number) => (
                              <li key={i}>{w}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}
