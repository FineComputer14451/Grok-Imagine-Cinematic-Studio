/**
 * Shared LIVE-PREVIEW OAuth client (server-only — NEVER import from the client).
 *
 * The sandbox serves each live preview on a dynamic `https://*.grok-sandbox.com`
 * URL, which can't be pre-registered per app. The broker instead exposes ONE
 * shared "preview" client that accepts any
 * `https://*.grok-sandbox.com/api/auth/oauth2/callback/*`
 * (broker: `app-builder-deployer/auth/src/preview-oauth.ts`). Baking it here lets
 * the live preview do REAL sign-in — no demo/mock users — with no platform
 * injection. When deployed the deployer injects a per-app
 * `GROK_AUTH_*` that overrides these (see `server.ts`).
 *
 * Live-preview client id/secret come from env (never commit the secret).
 * Deployer injects `GROK_AUTH_CLIENT_ID` / `GROK_AUTH_CLIENT_SECRET`.
 * Optional sandbox fallback: `GROK_PREVIEW_CLIENT_ID` / `GROK_PREVIEW_CLIENT_SECRET`.
 */
function readEnv(name: string): string {
  const value = process.env[name]?.trim();
  return value ? value : "";
}

export const PREVIEW_CLIENT_ID =
  readEnv("GROK_PREVIEW_CLIENT_ID") || "grok_preview";
export const PREVIEW_CLIENT_SECRET = readEnv("GROK_PREVIEW_CLIENT_SECRET");

/** The shared auth broker issuer (OIDC discovery lives under it). */
export const GROK_ISSUER_DEFAULT = "https://auth.grok.me";

/**
 * Host patterns whose callbacks the preview client accepts. Better Auth derives
 * the live preview's real origin from the request host and validates it against
 * this list (wildcard-matched), so the OAuth `redirect_uri` becomes the concrete
 * `https://<preview-host>/api/auth/oauth2/callback/...` the broker allows.
 */
export const PREVIEW_ALLOWED_HOSTS = ["*.grok-sandbox.com"] as const;
