"use client";

/**
 * Premium landing page — AI Interviewer hero.
 */

import Link from "next/link";
import { Navbar } from "@/components/layout/navbar";

export default function HomePage() {
  return (
    <>
      <Navbar />

      <main className="flex-1 relative overflow-hidden">
        {/* Ambient glow orbs */}
        <div
          className="glow-orb glow-orb-primary"
          style={{ width: 500, height: 500, top: "-10%", left: "-5%" }}
        />
        <div
          className="glow-orb glow-orb-secondary"
          style={{ width: 400, height: 400, bottom: "5%", right: "-5%" }}
        />

        {/* Hero */}
        <section className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-24 pb-32">
          <div className="text-center max-w-4xl mx-auto">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-glass-border bg-glass-bg text-sm text-foreground-muted mb-8 animate-fade-in-up opacity-0">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
              AI-Powered Interview Preparation
            </div>

            {/* Heading */}
            <h1
              className="font-[var(--font-outfit)] text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.1] mb-6 animate-fade-in-up opacity-0 animate-delay-100"
            >
              Ace your next interview with{" "}
              <span className="gradient-text">evidence-driven</span>{" "}
              AI practice
            </h1>

            {/* Subheading */}
            <p
              className="text-lg sm:text-xl text-foreground-muted max-w-2xl mx-auto mb-10 leading-relaxed animate-fade-in-up opacity-0 animate-delay-200"
            >
              Practice with an AI interviewer that researches your target role
              and company, analyzes real interview patterns, and conducts
              realistic, adaptive interviews — just like the real thing.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up opacity-0 animate-delay-300">
              <Link href="/register" className="btn-primary text-base px-8 py-3.5">
                <span>Start Practicing Free</span>
              </Link>
              <Link href="/login" className="btn-secondary text-base px-8 py-3.5">
                Sign In
              </Link>
            </div>
          </div>

          {/* Feature cards */}
          <div className="mt-28 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in-up opacity-0 animate-delay-400">
            <FeatureCard
              icon={
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                </svg>
              }
              title="Adaptive Intelligence"
              description="Questions adapt in real-time based on your answers. Strong responses increase difficulty; weak areas get probing follow-ups."
            />
            <FeatureCard
              icon={
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m5.231 13.481L15 17.25m-4.5-15H5.625c-.621 0-1.125.504-1.125 1.125v16.5c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9zm3.75 11.625a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
                </svg>
              }
              title="Evidence-Based Questions"
              description="Every question is backed by role research, organization intelligence, and real interview patterns — not generic prompts."
            />
            <FeatureCard
              icon={
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
                </svg>
              }
              title="Voice-First Experience"
              description="Talk through your answers naturally. The AI interviewer listens, evaluates, and responds — just like a human interviewer."
            />
          </div>

          {/* Two modes section */}
          <div className="mt-28">
            <h2 className="font-[var(--font-outfit)] text-3xl sm:text-4xl font-bold text-center mb-4">
              Two ways to prepare
            </h2>
            <p className="text-foreground-muted text-center mb-12 max-w-xl mx-auto">
              Whether you want targeted practice or a full simulation,
              every session feels like a real interview.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
              {/* Focused Practice Card */}
              <div className="glass-card p-8 group cursor-pointer pulse-glow">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-brand-primary/20 to-brand-secondary/20 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                  <svg className="w-6 h-6 text-brand-accent" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.57 50.57 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342" />
                  </svg>
                </div>
                <h3 className="font-[var(--font-outfit)] text-xl font-semibold mb-2">
                  Focused Practice
                </h3>
                <p className="text-foreground-muted text-sm leading-relaxed mb-4">
                  Choose a specific category — Technical, Behavioral, Case Study,
                  or more — and practice through an adaptive interview focused on
                  that area.
                </p>
                <div className="flex flex-wrap gap-2">
                  {["Technical", "Behavioral", "System Design", "Case Study"].map(
                    (tag) => (
                      <span
                        key={tag}
                        className="text-xs px-2.5 py-1 rounded-full border border-glass-border text-foreground-dim"
                      >
                        {tag}
                      </span>
                    )
                  )}
                </div>
              </div>

              {/* Real Interview Simulation Card */}
              <div className="glass-card p-8 group cursor-pointer pulse-glow">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-brand-secondary/20 to-brand-accent/20 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                  <svg className="w-6 h-6 text-brand-accent" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.59 14.37a6 6 0 0 1-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 0 0 6.16-12.12A14.98 14.98 0 0 0 9.631 8.41m5.96 5.96a14.926 14.926 0 0 1-5.841 2.58m-.119-8.54a6 6 0 0 0-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 0 0-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 0 1-2.448-2.448 14.9 14.9 0 0 1 .06-.312m-2.24 2.39a4.493 4.493 0 0 0-1.757 4.306 4.493 4.493 0 0 0 4.306-1.758M16.5 9a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Z" />
                  </svg>
                </div>
                <h3 className="font-[var(--font-outfit)] text-xl font-semibold mb-2">
                  Real Interview Simulation
                </h3>
                <p className="text-foreground-muted text-sm leading-relaxed mb-4">
                  Experience a full-length interview where the AI dynamically
                  determines the structure based on your target role and company
                  research.
                </p>
                <div className="flex flex-wrap gap-2">
                  {["Role Research", "Company Intel", "Adaptive Flow", "Full Report"].map(
                    (tag) => (
                      <span
                        key={tag}
                        className="text-xs px-2.5 py-1 rounded-full border border-glass-border text-foreground-dim"
                      >
                        {tag}
                      </span>
                    )
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-glass-border py-8">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <p className="text-center text-sm text-foreground-dim">
              © {new Date().getFullYear()} AI Interviewer. Built for candidates
              who want to practice like it&apos;s the real thing.
            </p>
          </div>
        </footer>
      </main>
    </>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="glass-card p-6 group">
      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-brand-primary/20 to-brand-secondary/20 flex items-center justify-center mb-4 text-brand-accent group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <h3 className="font-[var(--font-outfit)] text-lg font-semibold mb-2">
        {title}
      </h3>
      <p className="text-foreground-muted text-sm leading-relaxed">
        {description}
      </p>
    </div>
  );
}
