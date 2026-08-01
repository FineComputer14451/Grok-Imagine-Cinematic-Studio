import { useEffect } from "react";
import { useStudioStore } from "@/lib/studio-store";

/** Hydrate store from Snapshot API once on mount; safe no-op if offline. */
export function ApiBootstrap() {
  const refreshFromApi = useStudioStore((s) => s.refreshFromApi);

  useEffect(() => {
    void refreshFromApi();
  }, [refreshFromApi]);

  return null;
}
