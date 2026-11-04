import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary-50 text-primary-700 border border-primary-200/60",
        success: "bg-emerald-50 text-emerald-700 border border-emerald-200/60",
        warning: "bg-amber-50 text-amber-700 border border-amber-200/60",
        error: "bg-red-50 text-red-700 border border-red-200/60",
        neutral: "bg-slate-100 text-slate-700 border border-slate-200/60",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
