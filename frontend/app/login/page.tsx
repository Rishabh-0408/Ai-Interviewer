"use client";

/**
 * Login page — email/password authentication via Firebase.
 */

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { Navbar } from "@/components/layout/navbar";

export default function LoginPage() {
  const { login, error, clearError, loading: authLoading } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setSubmitting(true);

    try {
      await login(email, password);
      router.push("/dashboard");
    } catch {
      // Error is set in auth provider
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <Navbar />

      <main className="flex-1 flex items-center justify-center relative px-4 py-16">
        {/* Background glow */}
        <div
          className="glow-orb glow-orb-primary"
          style={{ width: 400, height: 400, top: "10%", left: "20%" }}
        />

        <div className="w-full max-w-md animate-fade-in-up opacity-0">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="font-[var(--font-outfit)] text-3xl font-bold mb-2">
              Welcome back
            </h1>
            <p className="text-foreground-muted">
              Sign in to continue your interview preparation
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="glass-card p-8 space-y-5">
            {error && (
              <div className="p-3 rounded-lg bg-error/10 border border-error/20 text-error text-sm">
                {error}
              </div>
            )}

            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-foreground-muted mb-1.5"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field"
                placeholder="you@example.com"
                autoComplete="email"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-foreground-muted mb-1.5"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-field"
                placeholder="••••••••"
                autoComplete="current-password"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>{submitting ? "Signing in..." : "Sign In"}</span>
            </button>

            <p className="text-center text-sm text-foreground-muted">
              Don&apos;t have an account?{" "}
              <Link
                href="/register"
                className="text-brand-accent hover:text-brand-primary transition-colors"
              >
                Create one
              </Link>
            </p>
          </form>
        </div>
      </main>
    </>
  );
}
