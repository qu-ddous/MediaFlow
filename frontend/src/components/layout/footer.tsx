import React from "react";
import Link from "next/link";
import { DownloadCloud, ShieldCheck, Cpu, HardDrive } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-slate-200/80 bg-white">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand info */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600 text-white">
                <DownloadCloud className="h-4 w-4" />
              </div>
              <span className="font-bold text-slate-900 tracking-tight">MediaFlow</span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">
              Universal media extraction and transcoding platform engineered with high-throughput FFmpeg pipelines and strict SSRF security.
            </p>
            <div className="flex items-center gap-3 text-xs text-slate-400">
              <span className="inline-flex items-center gap-1">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" /> SSRF Protected
              </span>
              <span className="inline-flex items-center gap-1">
                <Cpu className="h-3.5 w-3.5 text-primary-500" /> FFmpeg 7.x
              </span>
            </div>
          </div>

          {/* Product links */}
          <div>
            <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-3">Product</h4>
            <ul className="space-y-2 text-xs text-slate-600">
              <li><Link href="/" className="hover:text-primary-600 transition-colors">Media Downloader</Link></li>
              <li><Link href="/converter" className="hover:text-primary-600 transition-colors">Format Converter</Link></li>
              <li><Link href="/history" className="hover:text-primary-600 transition-colors">Download History</Link></li>
              <li><Link href="/sources" className="hover:text-primary-600 transition-colors">Supported Sources</Link></li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-3">Resources</h4>
            <ul className="space-y-2 text-xs text-slate-600">
              <li><Link href="/faq" className="hover:text-primary-600 transition-colors">Frequently Asked Questions</Link></li>
              <li><Link href="/sources" className="hover:text-primary-600 transition-colors">Compliance & Permissions</Link></li>
              <li><a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="hover:text-primary-600 transition-colors">API Documentation</a></li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-3">Legal & Privacy</h4>
            <ul className="space-y-2 text-xs text-slate-600">
              <li><Link href="/privacy" className="hover:text-primary-600 transition-colors">Privacy Policy</Link></li>
              <li><Link href="/terms" className="hover:text-primary-600 transition-colors">Terms of Service</Link></li>
              <li><Link href="/contact" className="hover:text-primary-600 transition-colors">Contact Support</Link></li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-4">
          <p>© {new Date().getFullYear()} MediaFlow. Authorized personal use and creative commons media only.</p>
          <p>Strictly compliant with source provider policies. Zero DRM circumvention.</p>
        </div>
      </div>
    </footer>
  );
}

