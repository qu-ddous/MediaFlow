import React from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-12 space-y-6">
      <Link href="/" className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary-600 hover:text-primary-700">
        <ArrowLeft className="h-3.5 w-3.5" /> Back to Home
      </Link>

      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Privacy Policy</h1>
      <p className="text-xs text-slate-400">Last updated: November 2026</p>

      <div className="prose prose-slate text-xs sm:text-sm text-slate-600 space-y-4">
        <p>
          MediaFlow operates with privacy as a foundational principle. We do not require registration for basic media downloading, do not harvest personal credentials, and do not store third-party login cookies or auth tokens.
        </p>

        <h3 className="text-base font-semibold text-slate-900 mt-6">1. Information We Collect</h3>
        <p>
          We only process the media URL provided during your active session. Request IP addresses are stored in temporary ephemeral access logs for rate-limiting, abuse mitigation, and SSRF prevention.
        </p>

        <h3 className="text-base font-semibold text-slate-900 mt-6">2. File Retention & Automated Deletion</h3>
        <p>
          Media files downloaded to server workspace directories are retained for a maximum of 24 hours. After this window, our background cleaner permanently purges all associated files and logs from disk.
        </p>

        <h3 className="text-base font-semibold text-slate-900 mt-6">3. Third-Party Requests</h3>
        <p>
          Outbound network requests are strictly dispatched to public stream sources requested by the user. MediaFlow does not pass user telemetry to third parties.
        </p>
      </div>
    </div>
  );
}

