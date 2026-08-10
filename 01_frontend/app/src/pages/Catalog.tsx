import { useState, useCallback } from "react";
import { useNavigate } from "react-router";
import { useCatalogPublications } from "@/hooks/usePublicationQuery";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
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
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  FileText,
  Filter,
} from "lucide-react";
import { format } from "date-fns";
import { publicationTypes } from "@/lib/schemas";
import type { ListCatalogParams } from "@/api/publication";

const SORT_OPTIONS = [
  { value: "published_at", label: "Date Published" },
  { value: "title", label: "Title" },
  { value: "publication_type", label: "Type" },
];

const PAGE_SIZE = 10;

export default function Catalog() {
  const navigate = useNavigate();

  const [search, setSearch] = useState("");
  const [liveSearch, setLiveSearch] = useState("");
  const [pubType, setPubType] = useState<string>("");
  const [sortBy, setSortBy] = useState("published_at");
  const [order, setOrder] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);

  const params: ListCatalogParams = {
    page,
    size: PAGE_SIZE,
    ...(search && { search }),
    ...(pubType && { publication_type: pubType }),
    ...(sortBy && { sort_by: sortBy }),
    ...(order && { order }),
  };

  const { data, isLoading, isError } = useCatalogPublications(params);

  const publications = data?.items ?? [];
  const totalPages = data?.pages ?? 1;
  const totalCount = data?.total ?? 0;

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

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-3">
            <BookOpen className="h-8 w-8 text-emerald-600" />
            Public Library
          </h1>
          <p className="text-slate-500 mt-2">
            Browse and search all published and archived publications across the network.
          </p>
        </div>
      </div>

      <Card className="border-slate-200 shadow-sm">
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4 items-center">
            {/* Search */}
            <div className="flex-1 relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search catalog by title, DOI..."
                className="pl-9 w-full"
                value={liveSearch}
                onChange={(e) => setLiveSearch(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              />
            </div>
            <Button onClick={handleSearch} variant="secondary">
              Search
            </Button>

            {/* Type Filter */}
            <div className="w-full md:w-48 flex items-center gap-2">
              <Filter className="h-4 w-4 text-slate-400" />
              <Select value={pubType || "ALL"} onValueChange={handleFilterChange(setPubType)}>
                <SelectTrigger>
                  <SelectValue placeholder="All Types" />
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

            {/* Sorting */}
            <div className="w-full md:w-56 flex items-center gap-2">
              <ArrowUpDown className="h-4 w-4 text-slate-400" />
              <Select
                value={sortBy}
                onValueChange={(val) => {
                  setSortBy(val);
                  setPage(1);
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  {SORT_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button variant="outline" size="icon" onClick={toggleOrder} title={`Currently: ${order.toUpperCase()}`}>
                <ArrowUpDown className={`h-4 w-4 ${order === "desc" ? "rotate-180" : ""}`} />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      <div className="space-y-4">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="border-slate-100 shadow-sm">
              <CardContent className="p-6">
                <Skeleton className="h-6 w-2/3 mb-4" />
                <Skeleton className="h-4 w-1/4" />
              </CardContent>
            </Card>
          ))
        ) : isError ? (
          <div className="p-8 text-center bg-red-50 text-red-600 rounded-lg border border-red-100">
            Failed to load catalog. Please try again.
          </div>
        ) : publications.length === 0 ? (
          <div className="p-12 text-center bg-slate-50 rounded-xl border border-dashed border-slate-200">
            <FileText className="h-12 w-12 mx-auto text-slate-300 mb-3" />
            <h3 className="text-lg font-medium text-slate-900">No publications found</h3>
            <p className="text-slate-500 mt-1">Try adjusting your search or filters.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            <div className="text-sm text-slate-500 mb-2">
              Showing {publications.length} of {totalCount} result{totalCount !== 1 ? "s" : ""}
            </div>
            {publications.map((pub) => (
              <Card
                key={pub.id}
                className="border-slate-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer group"
                onClick={() => navigate(`/dashboard/catalog/${pub.id}`)}
              >
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start gap-4">
                    <div>
                      <CardTitle className="text-xl group-hover:text-emerald-600 transition-colors">
                        {pub.title}
                      </CardTitle>
                      <CardDescription className="mt-1 flex items-center gap-2">
                        <span>{pub.publication_type.replace("_", " ")}</span>
                        {pub.doi && (
                          <>
                            <span>•</span>
                            <span>DOI: {pub.doi}</span>
                          </>
                        )}
                        {pub.published_at && (
                          <>
                            <span>•</span>
                            <span>{format(new Date(pub.published_at), "MMM d, yyyy")}</span>
                          </>
                        )}
                      </CardDescription>
                    </div>
                    <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                      View Details
                    </Button>
                  </div>
                </CardHeader>
              </Card>
            ))}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-2 mt-8">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Previous
                </Button>
                <span className="text-sm text-slate-600 px-4">
                  Page {page} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
