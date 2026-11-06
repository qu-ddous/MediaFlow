import React from "react";
import { LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded-2xl bg-white border border-slate-200/80 shadow-sm">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-400 mb-4">
        <Icon className="h-7 w-7" />
      </div>
      <h4 className="text-base font-bold text-slate-800">{title}</h4>
      <p className="text-xs text-slate-500 mt-1.5 max-w-sm leading-relaxed">{description}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} size="sm" className="mt-5 text-xs">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

