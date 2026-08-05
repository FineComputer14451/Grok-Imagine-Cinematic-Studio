import { createFileRoute } from "@tanstack/react-router";
import {
  fetchRemoteCatalog,
  mergeRemoteCatalog,
} from "@/lib/github-catalog";

export const Route = createFileRoute("/api/catalog")({
  server: {
    handlers: {
      GET: async () => {
        try {
          const remote = await fetchRemoteCatalog();
          const merged = mergeRemoteCatalog(remote.marketplace, remote.plugin);
          return Response.json({
            ok: true,
            marketplace: merged.marketplace,
            plugins: merged.plugins,
            version: merged.version,
            pinSha: merged.pinSha,
            fetchedAt: merged.fetchedAt,
          });
        } catch (err) {
          const message =
            err instanceof Error ? err.message : "Failed to sync catalog";
          return Response.json(
            { ok: false, error: message },
            { status: 502 },
          );
        }
      },
    },
  },
});
