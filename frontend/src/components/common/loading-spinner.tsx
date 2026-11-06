import React from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  label?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function LoadingSpinner({
  label,
  size = "md",
  className,
}: LoadingSpinnerProps) {
  const sizes = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-10 w-10",
  };

  return (
    <div className={cn("flex flex-col items-center justify-center p-6 gap-2", className)}>
      <Loader2 className={cn("animate-spin text-primary-600", sizes[size])} />
      {label && <p className="text-xs text-slate-500 font-medium">{label}</p>}
    </div>
  );
}

