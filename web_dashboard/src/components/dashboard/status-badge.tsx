import { Badge } from "@/components/ui/badge";
import type { ShotStatus } from "@/lib/studio-data";

const labels: Record<ShotStatus, string> = {
  ready: "Ready",
  rendering: "Rendering",
  queued: "Queued",
  failed: "Failed",
  draft: "Draft",
};

export function StatusBadge({ status }: { status: ShotStatus }) {
  return <Badge variant={status}>{labels[status]}</Badge>;
}
