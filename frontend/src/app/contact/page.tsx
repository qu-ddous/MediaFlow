import React from "react";
import Link from "next/link";
import { ArrowLeft, Mail, MessageSquare, ShieldCheck } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function ContactPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-12 space-y-6">
      <Link href="/" className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary-600 hover:text-primary-700">
        <ArrowLeft className="h-3.5 w-3.5" /> Back to Home
      </Link>

      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Contact & Support</h1>
      <p className="text-xs text-slate-500">
        Need technical assistance, bug reports, or legal inquiries regarding MediaFlow?
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4">
        <Card>
          <CardHeader>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-50 text-primary-600 mb-2">
              <Mail className="h-5 w-5" />
            </div>
            <CardTitle className="text-base">Technical Support</CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-slate-600 space-y-2">
            <p>For engine bugs, failed transcodes, or platform suggestions:</p>
            <p className="font-semibold text-slate-900">support@mediaflow.local</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 mb-2">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <CardTitle className="text-base">Compliance & DMCA</CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-slate-600 space-y-2">
            <p>For takedown notices or copyright concerns:</p>
            <p className="font-semibold text-slate-900">compliance@mediaflow.local</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

