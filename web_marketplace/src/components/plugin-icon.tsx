import {
  Camera,
  Clapperboard,
  Cpu,
  Film,
  Package,
  ShieldAlert,
  Sparkles,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";

const ICONS: Record<string, LucideIcon> = {
  clapperboard: Clapperboard,
  cpu: Cpu,
  camera: Camera,
  film: Film,
  "shield-alert": ShieldAlert,
  sparkles: Sparkles,
  package: Package,
};

export function PluginIcon({
  name,
  className,
}: {
  name: string;
  className?: string;
}) {
  const Icon = ICONS[name] ?? Package;
  return <Icon className={cn("size-5", className)} aria-hidden />;
}
