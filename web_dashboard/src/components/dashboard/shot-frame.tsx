import { cn } from "@/lib/utils";
import type { AspectRatio, ShotStatus } from "@/lib/studio-data";
import { Clapperboard, Film, ImageIcon, Loader2 } from "lucide-react";

const aspectClass: Record<AspectRatio, string> = {
  "16:9": "aspect-video",
  "9:16": "aspect-[9/16]",
  "1:1": "aspect-square",
  "2.39:1": "aspect-[2.39/1]",
  "4:3": "aspect-[4/3]",
};

export function ShotFrame({
  frame,
  aspect = "16:9",
  status,
  mode,
  title,
  className,
  compact,
}: {
  frame: string;
  aspect?: AspectRatio;
  status?: ShotStatus;
  mode?: "image" | "video" | "storyboard";
  title?: string;
  className?: string;
  compact?: boolean;
}) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-lg border border-border bg-bg-elevated",
        aspectClass[aspect],
        className,
      )}
    >
      <div className={cn("absolute inset-0 film-grain", frame)} />
      <div className="absolute inset-0 bg-gradient-to-t from-bg/80 via-transparent to-bg/20" />

      {/* Letterbox marks for anamorphic */}
      {aspect === "2.39:1" && (
        <>
          <div className="absolute left-0 top-0 h-full w-px bg-fg/10" />
          <div className="absolute right-0 top-0 h-full w-px bg-fg/10" />
        </>
      )}

      {/* Center crosshair for draft / compose feel */}
      {(status === "draft" || status === "queued") && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-px w-8 bg-fg/20" />
          <div className="absolute h-8 w-px bg-fg/20" />
        </div>
      )}

      {status === "rendering" && (
        <div className="absolute inset-0 flex items-center justify-center bg-bg/40 backdrop-blur-[1px]">
          <Loader2 className="size-5 animate-spin text-fg-muted" />
        </div>
      )}

      {status === "failed" && (
        <div className="absolute inset-0 flex items-center justify-center bg-danger/10">
          <span className="rounded-full border border-danger/30 bg-bg/70 px-2 py-0.5 text-xs text-danger">
            Failed
          </span>
        </div>
      )}

      <div className="absolute bottom-0 left-0 right-0 flex items-end justify-between gap-2 p-2.5">
        {title && !compact ? (
          <span className="truncate text-xs font-medium text-fg/90">{title}</span>
        ) : (
          <span />
        )}
        <div className="flex items-center gap-1.5">
          {mode === "video" ? (
            <Film className="size-3 text-fg-muted" />
          ) : mode === "storyboard" ? (
            <Clapperboard className="size-3 text-fg-muted" />
          ) : (
            <ImageIcon className="size-3 text-fg-muted" />
          )}
        </div>
      </div>
    </div>
  );
}
