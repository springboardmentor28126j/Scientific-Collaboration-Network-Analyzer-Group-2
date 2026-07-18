import { useNavigate } from "react-router";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, FileText, Clock, CheckCircle2, ArrowRight } from "lucide-react";
import { usePublications } from "@/hooks/usePublicationQuery";
import { CreatePublicationDialog } from "@/components/CreatePublicationDialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { format } from "date-fns";

const STATUS_STYLES: Record<string, string> = {
  DRAFT:              "bg-slate-100 text-slate-700 border-slate-200",
  SUBMITTED:          "bg-blue-50 text-blue-700 border-blue-200",
  UNDER_REVIEW:       "bg-amber-50 text-amber-700 border-amber-200",
  REVISION_REQUIRED:  "bg-orange-50 text-orange-700 border-orange-200",
  ACCEPTED:           "bg-emerald-50 text-emerald-700 border-emerald-200",
  REJECTED:           "bg-red-50 text-red-700 border-red-200",
  PUBLISHED:          "bg-purple-50 text-purple-700 border-purple-200",
  ARCHIVED:           "bg-gray-100 text-gray-600 border-gray-200",
};

export default function Researcher() {
  const navigate = useNavigate();

  // Show recent publications in a compact form for the dashboard
  const { data, isLoading } = usePublications({ page: 1, size: 5, sort_by: "created_at", order: "desc" });
  const { data: draftData }     = usePublications({ status: "DRAFT" });
  const { data: submittedData } = usePublications({ status: "SUBMITTED" });
  const { data: reviewData }    = usePublications({ status: "UNDER_REVIEW" });
  const { data: publishedData } = usePublications({ status: "PUBLISHED" });

  const publications   = data?.items ?? [];
  const draftCount     = draftData?.total ?? 0;
  const submittedCount = submittedData?.total ?? 0;
  const reviewCount    = reviewData?.total ?? 0;
  const publishedCount = publishedData?.total ?? 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-emerald-600" />
            My Research
          </h1>
          <p className="text-slate-500 mt-1 text-sm">
            Manage your research papers and track submissions
          </p>
        </div>
        <CreatePublicationDialog />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Drafts</CardDescription>
            <CardTitle className="text-3xl font-bold">{draftCount}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <FileText className="h-4 w-4" />
              <span>In progress</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Submitted</CardDescription>
            <CardTitle className="text-3xl font-bold">{submittedCount}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-sm text-blue-600">
              <FileText className="h-4 w-4" />
              <span>Awaiting review</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Under Review</CardDescription>
            <CardTitle className="text-3xl font-bold">{reviewCount}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-sm text-amber-600">
              <Clock className="h-4 w-4" />
              <span>Being reviewed</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Published</CardDescription>
            <CardTitle className="text-3xl font-bold">{publishedCount}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-sm text-emerald-600">
              <CheckCircle2 className="h-4 w-4" />
              <span>Live</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent publications */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <div>
            <CardTitle className="text-base">Recent Publications</CardTitle>
            <CardDescription className="text-xs mt-0.5">Your 5 most recently created papers</CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate("/dashboard/publications")}
            className="shrink-0"
          >
            View All <ArrowRight className="h-4 w-4 ml-1" />
          </Button>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="p-3 border rounded-lg flex justify-between items-center">
                  <div className="space-y-1.5 flex-1">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-1/3" />
                  </div>
                  <Skeleton className="h-5 w-20 ml-4" />
                </div>
              ))}
            </div>
          ) : publications.length === 0 ? (
            <div className="text-center py-12 border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-lg">
              <BookOpen className="h-10 w-10 text-slate-300 mx-auto mb-3" />
              <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">No publications yet</h3>
              <p className="text-xs text-slate-500">Create your first publication to get started.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {publications.map((pub) => (
                <div
                  key={pub.id}
                  onClick={() => navigate(`/dashboard/publications/${pub.id}`)}
                  className="group p-3 border rounded-lg hover:border-emerald-400 hover:shadow-sm transition-all cursor-pointer flex items-center justify-between gap-4"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm text-slate-900 dark:text-white group-hover:text-emerald-600 transition-colors line-clamp-1">
                      {pub.title}
                    </p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {pub.publication_type.replace(/_/g, " ")} &bull; {format(new Date(pub.created_at), "MMM d, yyyy")}
                    </p>
                  </div>
                  <Badge
                    variant="outline"
                    className={`text-xs shrink-0 ${STATUS_STYLES[pub.status] ?? ""}`}
                  >
                    {pub.status.replace(/_/g, " ")}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
