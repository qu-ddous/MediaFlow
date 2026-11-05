"use client";

import React, { useEffect } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Application error:", error);
  }, [error]);

  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center p-4 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-red-50 text-red-500 mb-4">
        <AlertCircle className="h-7 w-7" />
      </div>
      <h2 className="text-xl font-bold text-slate-900">Something went wrong</h2>
      <p className="text-xs text-slate-500 mt-1 max-w-sm">
        {error.message || "An unexpected error occurred during execution. Please try again."}
      </p>
      <div className="mt-6 flex gap-3">
        <Button onClick={() => reset()} size="sm">
          <RefreshCw className="h-3.5 w-3.5 mr-2" /> Try Again
        </Button>
      </div>
    </div>
  );
}

