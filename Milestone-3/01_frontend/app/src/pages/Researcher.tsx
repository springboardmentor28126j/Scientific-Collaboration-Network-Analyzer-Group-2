import { useAuthStore } from "@/stores/authStore";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, FileText, Upload, Clock, CheckCircle2 } from "lucide-react";

export default function Researcher() {
  const user = useAuthStore((state) => state.user);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <BookOpen className="h-6 w-6" />
          My Research
        </h1>
        <p className="text-slate-500 mt-1">
          Manage your research papers and submissions
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Submitted</CardDescription>
            <CardTitle className="text-3xl font-bold">0</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-sm text-blue-600">
              <FileText className="h-4 w-4" />
              <span>Research papers</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Under Review</CardDescription>
            <CardTitle className="text-3xl font-bold">0</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-sm text-amber-600">
              <Clock className="h-4 w-4" />
              <span>In progress</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Approved</CardDescription>
            <CardTitle className="text-3xl font-bold">0</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-sm text-emerald-600">
              <CheckCircle2 className="h-4 w-4" />
              <span>Published</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Submit Research Paper</CardTitle>
          <CardDescription>
            Upload your research paper for review
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-lg p-12 text-center hover:border-emerald-400 transition-colors cursor-pointer">
            <Upload className="h-10 w-10 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">
              Coming Soon
            </h3>
            <p className="text-sm text-slate-500 max-w-sm mx-auto">
              The research submission feature will be available soon. Contact your institution admin for updates.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Researcher Info</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm">
            <span className="font-medium">Name:</span> {user?.full_name}
          </p>
          <p className="text-sm">
            <span className="font-medium">Email:</span> {user?.email}
          </p>
          <p className="text-sm">
            <span className="font-medium">Institution ID:</span>{" "}
            <span className="font-mono text-xs">{user?.institution_id}</span>
          </p>
          <p className="text-sm">
            <span className="font-medium">Role:</span>{" "}
            <span className="capitalize">{user?.role.toLowerCase().replace("_", " ")}</span>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
