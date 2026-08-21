import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router";
import { useVerifyEmail } from "@/hooks/useAuthQuery";
import { FlaskConical, CheckCircle2, XCircle, Loader2 } from "lucide-react";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const verifyMutation = useVerifyEmail();
  const [hasAttempted, setHasAttempted] = useState(false);

  useEffect(() => {
    if (token && !hasAttempted) {
      setHasAttempted(true);
      verifyMutation.mutate(token);
    }
  }, [token, hasAttempted]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-4">
      <div className="w-full max-w-md text-center">
        <div className="flex items-center justify-center gap-2 mb-8">
          <FlaskConical className="h-8 w-8 text-emerald-600" />
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">ResearchMesh</h1>
        </div>

        {!token ? (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <XCircle className="h-8 w-8 text-red-600" />
            </div>
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
              Invalid Verification Link
            </h2>
            <p className="text-slate-500 mb-4">
              The verification token is missing.
            </p>
            <Link
              to="/login"
              className="text-emerald-600 hover:text-emerald-700 hover:underline"
            >
              Go to login
            </Link>
          </div>
        ) : verifyMutation.isPending ? (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8">
            <Loader2 className="h-12 w-12 text-emerald-600 animate-spin mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
              Verifying your email...
            </h2>
            <p className="text-slate-500">Please wait while we verify your email address.</p>
          </div>
        ) : verifyMutation.isSuccess ? (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8">
            <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle2 className="h-8 w-8 text-emerald-600" />
            </div>
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
              Email Verified!
            </h2>
            <p className="text-slate-500 mb-4">
              Your email has been verified successfully. Your account is now active.
            </p>
            <Link
              to="/login"
              className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
            >
              Go to Login
            </Link>
          </div>
        ) : (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <XCircle className="h-8 w-8 text-red-600" />
            </div>
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
              Verification Failed
            </h2>
            <p className="text-slate-500 mb-4">
              {verifyMutation.error?.message || "The verification link is invalid or has expired."}
            </p>
            <Link
              to="/login"
              className="text-emerald-600 hover:text-emerald-700 hover:underline"
            >
              Go to login
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
