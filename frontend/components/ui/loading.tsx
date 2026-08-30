"use client";

/**
 * Loading spinner component with ambient glow effect.
 */

export function Loading({ text = "Loading..." }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12">
      <div className="relative">
        {/* Outer glow ring */}
        <div className="absolute inset-0 rounded-full bg-brand-primary/20 blur-xl animate-pulse" />

        {/* Spinner */}
        <div className="relative w-10 h-10 border-2 border-glass-border rounded-full">
          <div
            className="absolute inset-0 rounded-full border-2 border-transparent border-t-brand-primary animate-spin"
          />
        </div>
      </div>

      <p className="text-foreground-muted text-sm">{text}</p>
    </div>
  );
}

/**
 * Full-page loading state.
 */
export function PageLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <Loading text="Loading..." />
    </div>
  );
}
