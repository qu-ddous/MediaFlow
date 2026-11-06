"use client";

import * as React from "react";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";
import { cn } from "@/lib/utils";

export type ToastType = "success" | "error" | "info";

export interface ToastMessage {
  id: string;
  title: string;
  description?: string;
  type: ToastType;
}

interface ToastProps {
  toast: ToastMessage;
  onDismiss: (id: string) => void;
}

export function ToastItem({ toast, onDismiss }: ToastProps) {
  const icons = {
    success: <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0" />,
    error: <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />,
    info: <Info className="h-5 w-5 text-primary-500 flex-shrink-0" />,
  };

  const borders = {
    success: "border-emerald-200 bg-white",
    error: "border-red-200 bg-white",
    info: "border-primary-200 bg-white",
  };

  return (
    <div
      className={cn(
        "pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-2xl border p-4 shadow-lg transition-all animate-slide-up",
        borders[toast.type]
      )}
      role="alert"
    >
      {icons[toast.type]}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-slate-900 leading-snug">{toast.title}</p>
        {toast.description && (
          <p className="mt-0.5 text-xs text-slate-500 leading-relaxed">{toast.description}</p>
        )}
      </div>
      <button
        onClick={() => onDismiss(toast.id)}
        className="rounded-lg p-1 text-slate-400 hover:text-slate-600 transition-colors"
        aria-label="Close toast"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

export function ToastContainer({
  toasts,
  onDismiss,
}: {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}) {
  return (
    <div
      aria-live="assertive"
      className="pointer-events-none fixed inset-0 z-50 flex flex-col items-end px-4 py-6 sm:p-6 gap-2"
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

