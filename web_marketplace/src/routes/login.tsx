import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowLeft, PackageOpen } from "lucide-react";
import { GROK_PROVIDERS, authEnabled, signIn } from "@/lib/auth/client";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/login")({
  component: Login,
});

function Login() {
  return (
    <main className="grid min-h-dvh place-items-center px-4 py-10">
      <div className="w-full max-w-sm space-y-6">
        <div className="space-y-3 text-center">
          <div className="mx-auto flex size-12 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)]">
            <PackageOpen className="size-5" />
          </div>
          <h1 className="text-xl font-semibold tracking-tight text-[var(--color-fg)]">
            Sign in
          </h1>
          <p className="text-sm text-[var(--color-fg-muted)]">
            Sync your studio library across sessions when signed in.
          </p>
        </div>

        <div className="space-y-2 rounded-[var(--radius-xl)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)] p-4">
          {authEnabled ? (
            GROK_PROVIDERS.map((p) => (
              <Button
                key={p.providerId}
                type="button"
                variant="secondary"
                className="h-11 w-full"
                onClick={() => signIn(p.providerId, { callbackURL: "/" })}
              >
                Continue with {p.label}
              </Button>
            ))
          ) : (
            <p className="py-4 text-center text-sm text-[var(--color-fg-muted)]">
              Sign-in is disabled.
            </p>
          )}
        </div>

        <Button variant="ghost" className="w-full" asChild>
          <Link to="/">
            <ArrowLeft className="size-4" />
            Back to marketplace
          </Link>
        </Button>
      </div>
    </main>
  );
}
