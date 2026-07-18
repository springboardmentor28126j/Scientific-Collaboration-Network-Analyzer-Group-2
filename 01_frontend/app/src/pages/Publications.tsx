import { useState, useCallback } from "react";
import { useNavigate } from "react-router";
import { usePublications } from "@/hooks/usePublicationQuery";
import { useAuthStore } from "@/stores/authStore";
import { useInstitutions } from "@/hooks/useAuthQuery";
import { CreatePublicationDialog } from "@/components/CreatePublicationDialog";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  BookOpen,
  Search,
  Download,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  SortAsc,
  SortDesc,
  FileText,
  Filter,
} from "lucide-react";
import { format } from "date-fns";
import { publicationTypes } from "@/lib/schemas";
import type { ListPublicationsParams } from "@/api/publication";

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

const SORT_OPTIONS = [
  { value: "created_at", label: "Date Created" },
  { value: "title",      label: "Title" },
  { value: "status",     label: "Status" },
  { value: "publication_type", label: "Type" },
];

const PAGE_SIZE = 10;

export default function Publications() {
  const navigate  = useNavigate();
  const user      = useAuthStore((s) => s.user);
  const isResearcher  = user?.role === "RESEARCHER";
  const isSuperAdmin  = user?.role === "SUPER_ADMIN";

  const { data: institutions } = useInstitutions();

  const [search,      setSearch]      = useState("");
  const [liveSearch,  setLiveSearch]  = useState("");
  const [status,      setStatus]      = useState<string>("");
  const [pubType,     setPubType]     = useState<string>("");
  const [sortBy,      setSortBy]      = useState("created_at");
  const [order,       setOrder]       = useState<"asc" | "desc">("desc");
  const [page,        setPage]        = useState(1);
  const [institutionId, setInstitutionId] = useState<string>("");

  const params: ListPublicationsParams = {
    page,
    size: PAGE_SIZE,
    ...(search        && { search }),
    ...(status        && { status }),
    ...(pubType       && { publication_type: pubType }),
    ...(sortBy        && { sort_by: sortBy }),
    ...(order         && { order }),
    ...(isSuperAdmin && institutionId && { institution_id: institutionId }),
  };

  const { data, isLoading, isError } = usePublications(params);

  const publications = data?.items ?? [];
  const totalPages   = data?.pages ?? 1;
  const totalCount   = data?.total ?? 0;

  const handleSearch = useCallback(() => {
    setSearch(liveSearch);
    setPage(1);
  }, [liveSearch]);

  const handleFilterChange = (setter: (v: string) => void) => (val: string) => {
    setter(val === "ALL" ? "" : val);
    setPage(1);
  };

  const toggleOrder = () => {
    setOrder((o) => (o === "asc" ? "desc" : "asc"));
    setPage(1);
  };

  const handleSortChange = (val: string) => {
    setSortBy(val);
    setPage(1);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-emerald-600" />
            Publications
          </h1>
          <p className="text-slate-500 mt-1 text-sm">
            {isSuperAdmin
              ? "Browse all publications across the platform"
              : user?.role === "INSTITUTION_ADMIN"
              ? "Publications from your institution"
              : user?.role === "REVIEWER"
              ? "Publications available for review"
              : "Manage your research publications"}
          </p>
        </div>
        {isResearcher && <CreatePublicationDialog />}
      </div>

      {/* Filters Card */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Filter className="h-4 w-4" /> Filters &amp; Search
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3">
            {/* Search row */}
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Search by title, DOI, or abstract..."
                  className="pl-8"
                  value={liveSearch}
                  onChange={(e) => setLiveSearch(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                />
              </div>
              <Button variant="secondary" onClick={handleSearch} className="shrink-0">
                Search
              </Button>
            </div>

            {/* Filter row */}
            <div className="flex flex-wrap gap-2">
              {/* Status */}
              <Select
                value={status || "ALL"}
                onValueChange={handleFilterChange(setStatus)}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ALL">All Statuses</SelectItem>
                  {["DRAFT","SUBMITTED","UNDER_REVIEW","REVISION_REQUIRED","ACCEPTED","REJECTED","PUBLISHED","ARCHIVED"].map((s) => (
                    <SelectItem key={s} value={s}>
                      {s.replace(/_/g, " ")}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Type */}
              <Select
                value={pubType || "ALL"}
                onValueChange={handleFilterChange(setPubType)}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ALL">All Types</SelectItem>
                  {publicationTypes.map((t) => (
                    <SelectItem key={t} value={t}>
                      {t.replace(/_/g, " ")}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Sort By */}
              <Select value={sortBy} onValueChange={handleSortChange}>
                <SelectTrigger className="w-[160px]">
                  <ArrowUpDown className="h-3.5 w-3.5 mr-1 text-slate-400" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {SORT_OPTIONS.map((o) => (
                    <SelectItem key={o.value} value={o.value}>
                      {o.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Order toggle */}
              <Button variant="outline" size="icon" onClick={toggleOrder} title={order === "asc" ? "Ascending" : "Descending"}>
                {order === "asc" ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />}
              </Button>

              {/* Institution filter — Super Admin only */}
              {isSuperAdmin && (
                <Select
                  value={institutionId || "ALL"}
                  onValueChange={handleFilterChange(setInstitutionId)}
                >
                  <SelectTrigger className="w-[200px]">
                    <SelectValue placeholder="All Institutions" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ALL">All Institutions</SelectItem>
                    {institutions?.map((inst) => (
                      <SelectItem key={inst.id} value={inst.id}>
                        {inst.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      <Card>
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base">Results</CardTitle>
            {!isLoading && (
              <CardDescription className="text-xs mt-0.5">
                {totalCount} publication{totalCount !== 1 ? "s" : ""} found
              </CardDescription>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {/* Loading skeletons */}
          {isLoading && (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="p-4 border rounded-lg flex items-center justify-between">
                  <div className="space-y-2 flex-1">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-1/2" />
                  </div>
                  <Skeleton className="h-6 w-24 ml-4" />
                </div>
              ))}
            </div>
          )}

          {/* Error state */}
          {isError && !isLoading && (
            <div className="text-center py-12">
              <FileText className="h-10 w-10 text-red-300 mx-auto mb-3" />
              <p className="text-slate-500 text-sm">Failed to load publications. Please try again.</p>
            </div>
          )}

          {/* Empty state */}
          {!isLoading && !isError && publications.length === 0 && (
            <div className="text-center py-16 border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-lg">
              <BookOpen className="h-12 w-12 text-slate-300 mx-auto mb-4" />
              <h3 className="text-base font-medium text-slate-700 dark:text-slate-300 mb-1">
                No publications found
              </h3>
              <p className="text-sm text-slate-500">
                {isResearcher
                  ? "Create your first publication to get started."
                  : "No publications match your current filters."}
              </p>
            </div>
          )}

          {/* Publication list */}
          {!isLoading && !isError && publications.length > 0 && (
            <div className="space-y-3">
              {publications.map((pub) => (
                <div
                  key={pub.id}
                  onClick={() => navigate(`/dashboard/publications/${pub.id}`)}
                  className="group p-4 border rounded-lg hover:border-emerald-400 hover:shadow-sm transition-all cursor-pointer flex items-start justify-between gap-4"
                >
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-slate-900 dark:text-white group-hover:text-emerald-600 transition-colors line-clamp-1">
                      {pub.title}
                    </h4>
                    {pub.abstract && (
                      <p className="text-sm text-slate-500 mt-1 line-clamp-1">{pub.abstract}</p>
                    )}
                    <div className="flex flex-wrap items-center gap-2 mt-2 text-xs text-slate-500">
                      <span className="font-medium text-slate-600">
                        {pub.publication_type.replace(/_/g, " ")}
                      </span>
                      <span>•</span>
                      <span>{format(new Date(pub.created_at), "MMM d, yyyy")}</span>
                      {pub.doi && (
                        <>
                          <span>•</span>
                          <span className="font-mono text-slate-400">DOI: {pub.doi}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2 shrink-0">
                    <Badge
                      variant="outline"
                      className={STATUS_STYLES[pub.status] ?? "bg-slate-100 text-slate-700"}
                    >
                      {pub.status.replace(/_/g, " ")}
                    </Badge>
                    {pub.pdf_url && (
                      <a
                        href={pub.pdf_url}
                        target="_blank"
                        rel="noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="text-xs flex items-center gap-1 text-emerald-600 hover:underline"
                      >
                        <Download className="h-3 w-3" /> PDF
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {!isLoading && totalPages > 1 && (
            <div className="flex items-center justify-between mt-6 pt-4 border-t">
              <p className="text-sm text-slate-500">
                Page {page} of {totalPages}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  <ChevronLeft className="h-4 w-4 mr-1" /> Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                >
                  Next <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
