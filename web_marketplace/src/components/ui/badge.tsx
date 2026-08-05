import type * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-[var(--color-bg-muted)] text-[var(--color-fg)]",
        muted:
          "border-[var(--color-border)] bg-transparent text-[var(--color-fg-muted)]",
        accent:
          "border-transparent bg-[var(--color-accent)] text-[var(--color-accent-fg)]",
        success:
          "border-transparent bg-[var(--color-success-dim)] text-[var(--color-success)]",
        warn: "border-transparent bg-[var(--color-warn-dim)] text-[var(--color-warn)]",
        danger:
          "border-transparent bg-[var(--color-danger-dim)] text-[var(--color-danger)]",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export function Badge({
  className,
  variant,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & VariantProps<typeof badgeVariants>) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
