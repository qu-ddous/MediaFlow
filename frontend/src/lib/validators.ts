import { z } from "zod";

export const urlAnalyzeSchema = z.object({
  url: z
    .string()
    .min(1, "Please enter a valid URL")
    .url("Please enter a valid URL (starting with http:// or https://)")
    .refine((url) => {
      try {
        const parsed = new URL(url);
        return parsed.protocol === "http:" || parsed.protocol === "https:";
      } catch {
        return false;
      }
    }, "Only HTTP and HTTPS URLs are supported"),
});

export const downloadOptionSchema = z.object({
  url: z.string().url(),
  format: z.string().min(1, "Please select an output format"),
  quality: z.string().min(1, "Please select a quality/resolution"),
});

export const conversionSchema = z.object({
  jobId: z.string().optional(),
  inputPath: z.string().optional(),
  outputFormat: z.string().min(1, "Target format is required"),
  resolution: z.string().optional(),
  audioQuality: z.string().optional(),
});
