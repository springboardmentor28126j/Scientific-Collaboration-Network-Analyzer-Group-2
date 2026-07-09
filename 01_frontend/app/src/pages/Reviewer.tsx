import { useAuthStore } from "@/stores/authStore";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ClipboardCheck, Clock, CheckCircle2, AlertCircle } from "lucide-react";

export default function Reviewer() {
  const user = useAuthStore((state) => state.user);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <ClipboardCheck className="h-6 w-6" />
          My Reviews
        </h1>
        <p className="text-slate-500 mt-1">
          Review assigned research papers and provide feedback
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Pending Reviews</CardDescription>
            <CardTitle className="text-3xl font-bold">0</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-sm text-amber-600">
              <Clock className="h-4 w-4" />
              <span>Needs your attention</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Completed</CardDescription>
            <CardTitle className="text-3xl font-bold">0</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-sm text-emerald-600">
              <CheckCircle2 className="h-4 w-4" />
              <span>Reviews done</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Overdue</CardDescription>
            <CardTitle className="text-3xl font-bold">0</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-sm text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span>Past deadline</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Assigned Papers</CardTitle>
          <CardDescription>
            Papers assigned to you for review
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <ClipboardCheck className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-1">
              No papers assigned yet
            </h3>
            <p className="text-sm text-slate-500 max-w-sm mx-auto">
              Research papers will appear here when assigned to you by the system.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Reviewer Info</CardTitle>
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
