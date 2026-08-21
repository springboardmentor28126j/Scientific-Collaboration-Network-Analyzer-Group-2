import { Link } from "react-router";
import { FlaskConical, Home } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-4">
      <div className="text-center">
        <div className="flex items-center justify-center gap-2 mb-8">
          <FlaskConical className="h-8 w-8 text-emerald-600" />
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">ResearchMesh</h1>
        </div>

        <div className="w-24 h-24 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-6">
          <span className="text-4xl font-bold text-slate-400">404</span>
        </div>

        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
          Page Not Found
        </h2>
        <p className="text-slate-500 mb-6 max-w-md mx-auto">
          The page you are looking for does not exist or you do not have permission to access it.
        </p>

        <div className="flex items-center justify-center gap-3">
          <Button asChild variant="outline">
            <Link to="/login">Sign In</Link>
          </Button>
          <Button asChild className="bg-emerald-600 hover:bg-emerald-700 gap-1">
            <Link to="/dashboard">
              <Home className="h-4 w-4" />
              Dashboard
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
