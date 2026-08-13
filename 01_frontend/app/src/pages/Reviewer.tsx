
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ClipboardCheck, Clock, CheckCircle2, ArrowRight } from "lucide-react";
import { useMyReviewAssignments } from "@/hooks/useReviewQuery";
import { usePublication } from "@/hooks/usePublicationQuery";
import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";
import { Link } from "react-router";

function AssignmentRow({ assignment }: { assignment: any }) {
  const { data: publication, isLoading } = usePublication(assignment.publication_id);

  if (isLoading) {
    return <div className="p-4 border-b animate-pulse bg-slate-50 h-16 rounded-md mb-2"></div>;
  }

  if (!publication) return null;

  return (
    <Link to={`/dashboard/publications/${publication.id}`} className="block transition hover:bg-slate-50 dark:hover:bg-slate-800 p-4 border rounded-lg mb-3">
      <div className="flex justify-between items-start">
        <div className="space-y-1">
          <h4 className="font-semibold text-slate-900 dark:text-slate-100 line-clamp-1">{publication.title}</h4>
          <p className="text-xs text-slate-500">Assigned: {format(new Date(assignment.assigned_at), "MMM d, yyyy")}</p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <Badge variant={assignment.status === "COMPLETED" ? "default" : "outline"} className={
            assignment.status === "COMPLETED" ? "bg-emerald-100 text-emerald-800 hover:bg-emerald-100" :
            assignment.status === "PENDING" ? "bg-amber-100 text-amber-800" : ""
          }>
            {assignment.status}
          </Badge>
          <ArrowRight className="w-4 h-4 text-slate-400" />
        </div>
      </div>
    </Link>
  );
}

export default function Reviewer() {
  const { data: assignments, isLoading } = useMyReviewAssignments();

  const pendingCount = assignments?.filter(a => a.status === "PENDING" || a.status === "IN_PROGRESS").length || 0;
  const completedCount = assignments?.filter(a => a.status === "COMPLETED").length || 0;

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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Pending Reviews</CardDescription>
            <CardTitle className="text-3xl font-bold">{pendingCount}</CardTitle>
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
            <CardTitle className="text-3xl font-bold">{completedCount}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-sm text-emerald-600">
              <CheckCircle2 className="h-4 w-4" />
              <span>Reviews done</span>
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
          {isLoading ? (
            <div className="p-8 text-center text-slate-500">Loading assignments...</div>
          ) : assignments?.length === 0 ? (
            <div className="text-center py-12">
              <ClipboardCheck className="h-12 w-12 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-1">
                No papers assigned yet
              </h3>
              <p className="text-sm text-slate-500 max-w-sm mx-auto">
                Research papers will appear here when assigned to you by the system.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {assignments?.sort((a, b) => new Date(b.assigned_at).getTime() - new Date(a.assigned_at).getTime()).map(assignment => (
                <AssignmentRow key={assignment.id} assignment={assignment} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
