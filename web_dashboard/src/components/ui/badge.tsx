import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "border-border bg-bg-subtle text-fg-muted",
        ready: "border-success/25 bg-success/10 text-success",
        rendering: "border-info/25 bg-info/10 text-info",
        queued: "border-warning/25 bg-warning/10 text-warning",
        failed: "border-danger/25 bg-danger/10 text-danger",
        draft: "border-border bg-muted text-fg-subtle",
        solid: "border-transparent bg-primary text-primary-fg",
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
