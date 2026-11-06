"use client";

import React, { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ToastContainer } from "@/components/ui/toast";
import { useToastStore } from "@/hooks/use-toast";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5000,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  const toasts = useToastStore((s) => s.toasts);
  const removeToast = useToastStore((s) => s.removeToast);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </QueryClientProvider>
  );
}

