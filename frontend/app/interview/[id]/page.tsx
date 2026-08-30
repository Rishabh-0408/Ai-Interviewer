"use client";

import { useState, useEffect, useRef, use } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api";
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Send,
  Sparkles,
  Clock,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Award,
  Loader2,
  XCircle,
  ChevronRight,
  TrendingUp,
} from "lucide-react";

interface QuestionData {
  id: string;
  order: number;
  question_text: string;
  question_type: string;
  competencies?: string[];
  is_followup?: boolean;
  probing_goal?: string;
  context_reasoning?: string;
}

interface EvaluationData {
  score: number;
  feedback: string;
  strengths?: string[];
  gaps?: string[];
}

export default function LiveInterviewRoom({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const interviewId = resolvedParams.id;

  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [interview, setInterview] = useState<any>(null);
  const [currentQuestion, setCurrentQuestion] = useState<QuestionData | null>(null);
  const [currentStage, setCurrentStage] = useState<{ order: number; total_stages: number; competency?: string } | null>(null);

  const [answerText, setAnswerText] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isAiSpeaking, setIsAiSpeaking] = useState(false);
  const [speechEnabled, setSpeechEnabled] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [latestEvaluation, setLatestEvaluation] = useState<EvaluationData | null>(null);

  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const recognitionRef = useRef<any>(null);

  // Timer
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Text-to-Speech
  const speakText = (text: string) => {
    if (!speechEnabled || typeof window === "undefined" || !("speechSynthesis" in window)) {
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.onstart = () => setIsAiSpeaking(true);
    utterance.onend = () => setIsAiSpeaking(false);
    utterance.onerror = () => setIsAiSpeaking(false);
    window.speechSynthesis.speak(utterance);
  };

  // Speech-to-Text setup
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = "en-US";

        recognition.onresult = (event: any) => {
          let transcript = "";
          for (let i = 0; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript + " ";
          }
          setAnswerText(transcript);
        };

        recognition.onerror = () => {
          setIsRecording(false);
        };

        recognition.onend = () => {
          setIsRecording(false);
        };

        recognitionRef.current = recognition;
      }
    }
  }, []);

  const toggleRecording = () => {
    if (!recognitionRef.current) {
      alert("Speech recognition is not supported in this browser. You can type your answer directly.");
      return;
    }

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsRecording(true);
      } catch (err) {
        setIsRecording(false);
      }
    }
  };

  // Fetch interview & start
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
      return;
    }

    if (user && interviewId) {
      setLoading(true);
      api.get<any>(`/api/v1/interviews/${interviewId}`)
        .then(async (data) => {
          setInterview(data);
          if (data.status === "completed") {
            router.push(`/reports/${interviewId}`);
            return;
          }

          // If interview is planned, start it to get first question
          if (data.status === "planned" || data.questions.length === 0) {
            const startRes = await api.post<any>(`/api/v1/interviews/${interviewId}/start`);
            setCurrentQuestion(startRes.question);
            setCurrentStage(startRes.current_stage);
            speakText(startRes.question.question_text);
          } else {
            // Pick last unanswered question
            const lastQ = data.questions[data.questions.length - 1];
            setCurrentQuestion({
              id: lastQ.id,
              order: lastQ.order,
              question_text: lastQ.question_text,
              question_type: lastQ.question_type,
              competencies: lastQ.competencies,
              is_followup: lastQ.is_followup,
            });
            speakText(lastQ.question_text);
          }
          setLoading(false);
        })
        .catch((err) => {
          setError(err instanceof Error ? err.message : "Failed to load interview");
          setLoading(false);
        });
    }
  }, [user, authLoading, interviewId, router]);

  const handleSubmitAnswer = async () => {
    if (!answerText.trim() || !currentQuestion) return;

    if (isRecording && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await api.post<any>(`/api/v1/interviews/${interviewId}/answer`, {
        question_id: currentQuestion.id,
        answer_text: answerText.trim(),
        duration_seconds: 45,
      });

      setLatestEvaluation(response.evaluation);

      if (response.action === "completed") {
        setTimeout(() => {
          router.push(`/reports/${interviewId}`);
        }, 1500);
      } else {
        // Next question or followup
        setCurrentQuestion(response.next_question);
        if (response.stage) setCurrentStage(response.stage);
        setAnswerText("");
        speakText(response.next_question.question_text);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to submit answer");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCompleteEarly = async () => {
    if (confirm("Are you sure you want to finish the interview and see your report now?")) {
      try {
        await api.post(`/api/v1/interviews/${interviewId}/complete`);
        router.push(`/reports/${interviewId}`);
      } catch {
        router.push(`/reports/${interviewId}`);
      }
    }
  };

  const formatTimer = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#090a14] text-white flex flex-col items-center justify-center">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center mb-4">
          <Sparkles className="w-8 h-8 text-indigo-400 animate-pulse" />
        </div>
        <p className="text-gray-300 font-medium">Entering AI Interview Room...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#090a14] text-white flex flex-col justify-between">
      {/* Top Bar */}
      <header className="border-b border-white/10 bg-[#0d0e1c]/80 backdrop-blur-xl px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center font-bold text-sm shadow-md">
            AI
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-semibold text-sm sm:text-base">{interview?.role || "Candidate Interview"}</h2>
              {interview?.company && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-300 border border-white/10">
                  {interview.company}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400 mt-0.5">
              <span className="capitalize">{interview?.mode} Mode</span>
              {currentStage && (
                <>
                  <span>•</span>
                  <span>Stage {currentStage.order} of {currentStage.total_stages}: {currentStage.competency}</span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs font-medium text-gray-300">
            <Clock className="w-3.5 h-3.5 text-indigo-400" />
            <span>{formatTimer(elapsedSeconds)}</span>
          </div>

          <button
            onClick={() => setSpeechEnabled(!speechEnabled)}
            className="p-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 transition-colors"
            title={speechEnabled ? "Mute AI Voice" : "Enable AI Voice"}
          >
            {speechEnabled ? <Volume2 className="w-4 h-4 text-indigo-400" /> : <VolumeX className="w-4 h-4 text-gray-500" />}
          </button>

          <button
            onClick={handleCompleteEarly}
            className="px-3.5 py-1.5 rounded-xl bg-red-500/15 hover:bg-red-500/25 border border-red-500/30 text-red-300 text-xs font-medium transition-colors"
          >
            Finish Early
          </button>
        </div>
      </header>

      {/* Main Room Arena */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-8 flex flex-col gap-6">
        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* AI Interviewer Avatar & Question Card */}
        <div className="p-6 rounded-3xl bg-gradient-to-b from-white/[0.04] to-white/[0.01] border border-white/10 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

          <div className="flex items-center gap-3 mb-4">
            {/* Pulsing Orb */}
            <div className="relative">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                  isAiSpeaking
                    ? "bg-indigo-500 text-white shadow-[0_0_20px_rgba(99,102,241,0.8)] scale-110"
                    : "bg-indigo-500/20 text-indigo-400"
                }`}
              >
                <Sparkles className="w-5 h-5" />
              </div>
              {isAiSpeaking && (
                <span className="absolute -top-1 -right-1 flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
                </span>
              )}
            </div>

            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">AI Interviewer</span>
                {currentQuestion?.is_followup && (
                  <span className="px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-[10px] uppercase font-bold tracking-wider">
                    Follow-up Probing
                  </span>
                )}
                {currentQuestion?.question_type && (
                  <span className="px-2 py-0.5 rounded-full bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 text-[10px] uppercase font-semibold">
                    {currentQuestion.question_type.replace("_", " ")}
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-400">
                {isAiSpeaking ? "Speaking..." : "Listening to your response"}
              </p>
            </div>
          </div>

          {/* Question Text */}
          <div className="mt-2 text-lg sm:text-xl font-medium text-gray-100 leading-relaxed">
            &ldquo;{currentQuestion?.question_text}&rdquo;
          </div>

          {currentQuestion?.competencies && currentQuestion.competencies.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-1.5">
              {currentQuestion.competencies.map((c, i) => (
                <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-white/5 border border-white/5 text-gray-400">
                  {c}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Real-time Feedback Banner (from previous turn) */}
        {latestEvaluation && (
          <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-3">
            <Award className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            <div className="text-xs sm:text-sm">
              <div className="font-semibold text-emerald-300 flex items-center gap-2">
                <span>Evaluator Score: {latestEvaluation.score}/100</span>
              </div>
              <p className="text-gray-300 mt-1">{latestEvaluation.feedback}</p>
            </div>
          </div>
        )}

        {/* Candidate Response Workspace */}
        <div className="p-6 rounded-3xl bg-white/[0.02] border border-white/10 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-gray-300 uppercase tracking-wider flex items-center gap-2">
              <span>Your Response</span>
              {isRecording && (
                <span className="flex items-center gap-1 text-red-400 text-xs normal-case animate-pulse font-normal">
                  <span className="w-2 h-2 rounded-full bg-red-500"></span> Live Transcribing
                </span>
              )}
            </label>

            <span className="text-xs text-gray-500">
              {answerText.trim() ? `${answerText.trim().split(/\s+/).length} words` : "Type or speak"}
            </span>
          </div>

          <textarea
            rows={5}
            placeholder="Type your answer, or click the microphone to speak naturally..."
            value={answerText}
            onChange={(e) => setAnswerText(e.target.value)}
            className="w-full px-4 py-3 rounded-2xl bg-[#121324] border border-white/10 focus:border-indigo-500 focus:outline-none text-sm sm:text-base leading-relaxed text-gray-100 placeholder-gray-500 resize-none transition-colors"
          />

          <div className="flex items-center justify-between pt-2">
            {/* Mic Toggle */}
            <button
              type="button"
              onClick={toggleRecording}
              className={`px-4 py-2.5 rounded-xl border font-medium text-xs sm:text-sm flex items-center gap-2 transition-all ${
                isRecording
                  ? "bg-red-500 text-white border-red-400 shadow-[0_0_20px_rgba(239,68,68,0.5)] animate-pulse"
                  : "bg-white/5 hover:bg-white/10 border-white/10 text-gray-300"
              }`}
            >
              {isRecording ? (
                <>
                  <MicOff className="w-4 h-4" />
                  <span>Stop Speaking</span>
                </>
              ) : (
                <>
                  <Mic className="w-4 h-4 text-indigo-400" />
                  <span>Speak Answer</span>
                </>
              )}
            </button>

            {/* Submit Turn */}
            <button
              type="button"
              disabled={isSubmitting || !answerText.trim()}
              onClick={handleSubmitAnswer}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-medium text-sm flex items-center gap-2 shadow-[0_0_25px_rgba(99,102,241,0.3)] transition-all disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Evaluating Answer...</span>
                </>
              ) : (
                <>
                  <span>Submit Answer</span>
                  <Send className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </main>

      {/* Footer Navigation Tip */}
      <footer className="py-4 text-center text-xs text-gray-500 border-t border-white/5">
        Pro-tip: Structure behavioral answers with STAR (Situation, Task, Action, Result) and articulate trade-offs in technical design.
      </footer>
    </div>
  );
}
