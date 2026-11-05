import React from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function TermsPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-12 space-y-6">
      <Link href="/" className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary-600 hover:text-primary-700">
        <ArrowLeft className="h-3.5 w-3.5" /> Back to Home
      </Link>

      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Terms of Service</h1>
      <p className="text-xs text-slate-400">Last updated: November 2026</p>

      <div className="prose prose-slate text-xs sm:text-sm text-slate-600 space-y-4">
        <p>
          By accessing and using MediaFlow, you agree to comply with and be bound by the following Terms of Service.
        </p>

        <h3 className="text-base font-semibold text-slate-900 mt-6">1. Permitted Use</h3>
        <p>
          MediaFlow is designed solely for accessing, transcribing, and downloading content you legally own, creative commons works, open educational materials, and publicly accessible media where authorized by applicable laws and provider policies.
        </p>

        <h3 className="text-base font-semibold text-slate-900 mt-6">2. Prohibited Activities</h3>
        <p>
          You agree not to use the platform to: (a) Circumvent DRM, encryption, or access paywalled media; (b) Transmit malicious files, exploits, or trigger network denial of service; (c) Probe internal IP networks (SSRF attacks); (d) Download copyright-infringing content without author permission.
        </p>

        <h3 className="text-base font-semibold text-slate-900 mt-6">3. Disclaimer of Warranties</h3>
        <p>
          The service is provided on an &quot;AS IS&quot; and &quot;AS AVAILABLE&quot; basis without warranties of any kind. MediaFlow does not claim universal compatibility with all third-party media sources.
        </p>
      </div>
    </div>
  );
}

