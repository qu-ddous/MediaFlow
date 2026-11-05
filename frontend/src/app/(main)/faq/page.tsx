import React from "react";
import { HelpCircle } from "lucide-react";

export default function FAQPage() {
  const faqs = [
    {
      q: "What is MediaFlow?",
      a: "MediaFlow is an enterprise-grade media analysis, download orchestration, and transcoding engine. It extracts authorized video/audio streams and allows users to convert them into standard container formats such as MP4, WebM, MP3, and WAV.",
    },
    {
      q: "Does MediaFlow store my downloaded media files indefinitely?",
      a: "No. All media assets are stored in isolated per-job directories on the processing server and are automatically pruned after 24 hours to safeguard your storage quota and privacy.",
    },
    {
      q: "Why did my download or analysis fail?",
      a: "Failures typically occur if: 1) The media is protected by Digital Rights Management (DRM); 2) The source requires login or authentication cookies; 3) The target IP violates SSRF security boundaries (e.g. localhost or private intranet); 4) The file size exceeds the 2 GB platform ceiling.",
    },
    {
      q: "How does FFmpeg transcoding work on MediaFlow?",
      a: "Our backend directly executes optimized FFmpeg 7 binary instances using argument arrays (strictly avoiding shell execution). It extracts video/audio streams, runs format remuxing or re-encoding, and streams live progress percentages to your browser via Server-Sent Events.",
    },
  ];

  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
          Frequently Asked Questions
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Detailed technical and legal questions about MediaFlow.
        </p>
      </div>

      <div className="space-y-4">
        {faqs.map((f, i) => (
          <div key={i} className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm space-y-2">
            <h3 className="text-sm font-semibold text-slate-900">{f.q}</h3>
            <p className="text-xs text-slate-600 leading-relaxed">{f.a}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

