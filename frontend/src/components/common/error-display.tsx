import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorDisplayProps {
  title?: string;
  message: string;
  suggestion?: string;
  onRetry?: () => void;
}

export function ErrorDisplay({
  title = "Something went wrong",
  message,
  suggestion,
  onRetry,
}: ErrorDisplayProps) {
  return (
    <div className="rounded-2xl border border-red-200/90 bg-red-50/70 p-5 text-left">
      <div className="flex items-start gap-3">
        <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-bold text-red-900">{title}</h4>
          <p className="mt-1 text-xs text-red-700 leading-relaxed">{message}</p>
          {suggestion && (
            <p className="mt-2 text-[11px] text-red-600 font-medium">
              💡 Tip: {suggestion}
            </p>
          )}
          {onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="mt-3 text-xs bg-white text-red-700 border-red-200 hover:bg-red-50"
            >
              <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
              Try Again
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

