import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { MediaInfo } from "@/types";

export function useAnalyzeUrl() {
  return useMutation<MediaInfo, Error, string>({
    mutationFn: (url: string) => api.analyzeUrl(url),
  });
}

