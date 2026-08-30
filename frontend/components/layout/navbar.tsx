"use client";

/**
 * Navbar component for the application.
 */

import Link from "next/link";
import { useAuth } from "@/providers/auth-provider";

export function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="sticky top-0 z-50 border-b border-glass-border bg-background/80 backdrop-blur-xl">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-primary to-brand-secondary flex items-center justify-center transition-transform group-hover:scale-110">
              <svg
                className="w-5 h-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z"
                />
              </svg>
            </div>
            <span className="font-[var(--font-outfit)] font-bold text-lg text-foreground">
              AI Interviewer
            </span>
          </Link>

          {/* Right side */}
          <div className="flex items-center gap-4">
            {user ? (
              <>
                <Link
                  href="/dashboard"
                  className="text-sm text-foreground-muted hover:text-foreground transition-colors"
                >
                  Dashboard
                </Link>
                <div className="h-4 w-px bg-glass-border" />
                <span className="text-sm text-foreground-dim">
                  {user.displayName || user.email}
                </span>
                <button
                  onClick={() => logout()}
                  className="btn-secondary !py-2 !px-4 text-sm"
                >
                  Sign Out
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="text-sm text-foreground-muted hover:text-foreground transition-colors"
                >
                  Sign In
                </Link>
                <Link href="/register" className="btn-primary !py-2 !px-4 text-sm">
                  <span>Get Started</span>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
