import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, FileText, Clock, CheckCircle2, Search } from "lucide-react";
import { usePublications } from "@/hooks/usePublicationQuery";
import { CreatePublicationDialog } from "@/components/CreatePublicationDialog";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";
import { useNavigate } from "react-router";
import { publicationTypes } from "@/lib/schemas";

const statusColors: Record<string, string> = {
  DRAFT: "bg-slate-100 text-slate-800",
  SUBMITTED: "bg-blue-100 text-blue-800",
  UNDER_REVIEW: "bg-amber-100 text-amber-800",
  REVISION_REQUIRED: "bg-orange-100 text-orange-800",
  ACCEPTED: "bg-emerald-100 text-emerald-800",
  REJECTED: "bg-red-100 text-red-800",
  PUBLISHED: "bg-purple-100 text-purple-800",
  ARCHIVED: "bg-gray-100 text-gray-800",
};

export default function Researcher() {
  const navigate = useNavigate();
  const { data: publications, isLoading } = usePublications();

  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [typeFilter, setTypeFilter] = useState<string>("ALL");
  const [search, setSearch] = useState("");

  const filteredPublications = publications?.filter((pub) => {
    const matchesStatus = statusFilter === "ALL" || pub.status === statusFilter;
    const matchesType = typeFilter === "ALL" || pub.publication_type === typeFilter;
    const matchesSearch = pub.title.toLowerCase().includes(search.toLowerCase());
    return matchesStatus && matchesType && matchesSearch;
  });

  const submittedCount = publications?.filter((p) => p.status === "SUBMITTED").length || 0;
  const underReviewCount = publications?.filter((p) => p.status === "UNDER_REVIEW").length || 0;
  const publishedCount = publications?.filter((p) => p.status === "PUBLISHED").length || 0;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <BookOpen className="h-6 w-6" />
            My Research
          </h1>
          <p className="text-slate-500 mt-1">
            Manage your research papers and submissions
          </p>
        </div>
        <CreatePublicationDialog />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Submitted</CardDescription>
            <CardTitle className="text-3xl font-bold">{submittedCount}</CardTitle>
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
            <CardTitle className="text-3xl font-bold">{underReviewCount}</CardTitle>
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
            <CardDescription>Published</CardDescription>
            <CardTitle className="text-3xl font-bold">{publishedCount}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-sm text-emerald-600">
              <CheckCircle2 className="h-4 w-4" />
              <span>Approved</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Publications</CardTitle>
          <CardDescription>
            View and manage all your research publications
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-slate-500" />
              <Input
                placeholder="Search publications..."
                className="pl-8"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">All Statuses</SelectItem>
                <SelectItem value="DRAFT">Draft</SelectItem>
                <SelectItem value="SUBMITTED">Submitted</SelectItem>
                <SelectItem value="UNDER_REVIEW">Under Review</SelectItem>
                <SelectItem value="REVISION_REQUIRED">Revision Required</SelectItem>
                <SelectItem value="ACCEPTED">Accepted</SelectItem>
                <SelectItem value="REJECTED">Rejected</SelectItem>
                <SelectItem value="PUBLISHED">Published</SelectItem>
                <SelectItem value="ARCHIVED">Archived</SelectItem>
              </SelectContent>
            </Select>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-full md:w-[180px]">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">All Types</SelectItem>
                {publicationTypes.map((t) => (
                  <SelectItem key={t} value={t}>
                    {t.replace("_", " ")}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {isLoading ? (
            <div className="text-center py-8 text-slate-500">Loading publications...</div>
          ) : filteredPublications?.length === 0 ? (
            <div className="text-center py-12 border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-lg">
              <BookOpen className="h-10 w-10 text-slate-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">
                No publications found
              </h3>
              <p className="text-sm text-slate-500">
                Create a new publication to get started.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredPublications?.map((pub) => (
                <div
                  key={pub.id}
                  onClick={() => navigate(`/dashboard/research/${pub.id}`)}
                  className="p-4 border rounded-lg hover:border-emerald-400 transition-colors cursor-pointer group flex items-center justify-between"
                >
                  <div>
                    <h4 className="font-semibold text-lg group-hover:text-emerald-600 transition-colors">
                      {pub.title}
                    </h4>
                    <div className="flex items-center gap-3 mt-2 text-sm text-slate-500">
                      <span>{pub.publication_type.replace("_", " ")}</span>
                      <span>•</span>
                      <span>{format(new Date(pub.created_at), "MMM d, yyyy")}</span>
                    </div>
                  </div>
                  <Badge className={statusColors[pub.status] || "bg-slate-100"}>
                    {pub.status.replace("_", " ")}
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
