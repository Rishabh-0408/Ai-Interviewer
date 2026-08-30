"use client";

/**
 * Registration page — create account via Firebase + sync to backend.
 */

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { Navbar } from "@/components/layout/navbar";

export default function RegisterPage() {
  const { register, error, clearError } = useAuth();
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setLocalError(null);

    if (password !== confirmPassword) {
      setLocalError("Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      setLocalError("Password must be at least 6 characters.");
      return;
    }

    setSubmitting(true);

    try {
      await register(email, password, name || undefined);
      router.push("/dashboard");
    } catch {
      // Error is set in auth provider
    } finally {
      setSubmitting(false);
    }
  };

  const displayError = localError || error;

  return (
    <>
      <Navbar />

      <main className="flex-1 flex items-center justify-center relative px-4 py-16">
        {/* Background glow */}
        <div
          className="glow-orb glow-orb-secondary"
          style={{ width: 400, height: 400, bottom: "10%", right: "15%" }}
        />

        <div className="w-full max-w-md animate-fade-in-up opacity-0">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="font-[var(--font-outfit)] text-3xl font-bold mb-2">
              Create your account
            </h1>
            <p className="text-foreground-muted">
              Start practicing with AI-powered interviews
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="glass-card p-8 space-y-5">
            {displayError && (
              <div className="p-3 rounded-lg bg-error/10 border border-error/20 text-error text-sm">
                {displayError}
              </div>
            )}

            <div>
              <label
                htmlFor="name"
                className="block text-sm font-medium text-foreground-muted mb-1.5"
              >
                Full Name
              </label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input-field"
                placeholder="John Doe"
                autoComplete="name"
              />
            </div>

            <div>
              <label
                htmlFor="register-email"
                className="block text-sm font-medium text-foreground-muted mb-1.5"
              >
                Email
              </label>
              <input
                id="register-email"
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
                htmlFor="register-password"
                className="block text-sm font-medium text-foreground-muted mb-1.5"
              >
                Password
              </label>
              <input
                id="register-password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-field"
                placeholder="••••••••"
                autoComplete="new-password"
              />
            </div>

            <div>
              <label
                htmlFor="confirm-password"
                className="block text-sm font-medium text-foreground-muted mb-1.5"
              >
                Confirm Password
              </label>
              <input
                id="confirm-password"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="input-field"
                placeholder="••••••••"
                autoComplete="new-password"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>{submitting ? "Creating account..." : "Create Account"}</span>
            </button>

            <p className="text-center text-sm text-foreground-muted">
              Already have an account?{" "}
              <Link
                href="/login"
                className="text-brand-accent hover:text-brand-primary transition-colors"
              >
                Sign in
              </Link>
            </p>
          </form>
        </div>
      </main>
    </>
  );
}
