import React from "react";
import { CheckCircle2, XCircle, ShieldCheck, Globe, Film, Music } from "lucide-react";

export default function SourcesPage() {
  const supported = [
    { name: "Direct Media URLs", type: "MP4, WebM, MKV, MP3, WAV, FLAC, OGG", status: "Full Support" },
    { name: "Public Video Platforms", type: "Vimeo, Dailymotion, Twitch Clips", status: "Public Videos" },
    { name: "Public Audio Feeds", type: "SoundCloud (Public tracks), Podcasts (RSS)", status: "Public Audio" },
    { name: "Creative Commons Streams", type: "Educational, Open Source & Archive Media", status: "Full Support" },
  ];

  const unsupported = [
    { reason: "DRM-Protected Content", note: "Spotify, Netflix, Disney+, Amazon Prime Video" },
    { reason: "Paywalled & Premium Media", note: "Subscription-only media files or restricted portals" },
    { reason: "Private & Unlisted Media", note: "Content requiring session logins, 2FA, or private credentials" },
  ];

  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
          Supported Sources & Compliance Policy
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          MediaFlow is strictly engineered for authorized media streams, open protocols, and personal archives.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Supported */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200/90 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-emerald-600">
            <CheckCircle2 className="h-5 w-5" />
            <h2 className="text-base font-semibold text-slate-900">Supported Sources</h2>
          </div>
          <div className="space-y-3">
            {supported.map((s, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-200/60 text-xs">
                <div className="flex justify-between font-semibold text-slate-900">
                  <span>{s.name}</span>
                  <span className="text-emerald-600">{s.status}</span>
                </div>
                <p className="text-slate-500 mt-1">{s.type}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Unsupported */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200/90 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-red-500">
            <XCircle className="h-5 w-5" />
            <h2 className="text-base font-semibold text-slate-900">Explicitly Prohibited / Unsupported</h2>
          </div>
          <div className="space-y-3">
            {unsupported.map((u, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-red-50/50 border border-red-100 text-xs">
                <p className="font-semibold text-red-700">{u.reason}</p>
                <p className="text-slate-500 mt-1">{u.note}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="p-5 rounded-2xl bg-primary-50 border border-primary-100 text-xs text-primary-900 flex items-start gap-3">
        <ShieldCheck className="h-5 w-5 text-primary-600 flex-shrink-0 mt-0.5" />
        <div>
          <p className="font-bold">Zero DRM Circumvention Guarantee</p>
          <p className="mt-1 leading-relaxed text-primary-800">
            MediaFlow respects Digital Rights Management (DRM) and provider terms of service. Our analyzer will reject encrypted or authentication-gated streams with clear error messages.
          </p>
        </div>
      </div>
    </div>
  );
}

