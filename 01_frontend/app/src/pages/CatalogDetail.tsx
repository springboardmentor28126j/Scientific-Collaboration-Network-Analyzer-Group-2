import { useNavigate, useParams } from "react-router";
import { useCatalogPublication, useDownloadPdf } from "@/hooks/usePublicationQuery";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, BookOpen, Download, User, Calendar, Tag, FileText, Link as LinkIcon, Building2 } from "lucide-react";
import { PublicationReferences } from "@/components/PublicationReferences";

export default function CatalogDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: publication, isLoading, isError } = useCatalogPublication(id!);
  const { mutateAsync: downloadPdf, isPending: isDownloading } = useDownloadPdf();

  if (isLoading) {
    return <div className="p-8 text-center text-slate-500">Loading publication details...</div>;
  }

  if (isError || !publication) {
    return <div className="p-8 text-center text-red-500">Publication not found</div>;
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-12">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/dashboard/catalog")}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white leading-tight">
            {publication.title}
          </h1>
          <div className="flex items-center gap-3 mt-3 text-sm text-slate-600">
            <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 font-medium border border-emerald-200">
              {publication.publication_type.replace("_", " ")}
            </span>
            {publication.year > 0 && (
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" /> {publication.year}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2 space-y-6">
          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="bg-slate-50/50 border-b border-slate-100">
              <CardTitle className="text-lg flex items-center gap-2">
                <FileText className="w-5 h-5 text-slate-500" />
                Overview
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              {publication.abstract && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Abstract</h3>
                  <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">
                    {publication.abstract}
                  </p>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Authors</h3>
                  <p className="text-slate-900 font-medium flex items-start gap-2">
                    <User className="w-4 h-4 mt-0.5 text-slate-400 shrink-0" />
                    {publication.authors || "Unknown Authors"}
                  </p>
                </div>

                {publication.institution_name && (
                  <div>
                    <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Institution</h3>
                    <p className="text-slate-900 flex items-start gap-2">
                      <Building2 className="w-4 h-4 mt-0.5 text-slate-400 shrink-0" />
                      {publication.institution_name}
                    </p>
                  </div>
                )}

                {publication.publication_name && (
                  <div>
                    <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Published In</h3>
                    <p className="text-slate-900 flex items-start gap-2">
                      <BookOpen className="w-4 h-4 mt-0.5 text-slate-400 shrink-0" />
                      {publication.publication_name}
                    </p>
                  </div>
                )}

                {publication.doi && (
                  <div>
                    <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">DOI</h3>
                    <p className="text-slate-900 flex items-start gap-2">
                      <Tag className="w-4 h-4 mt-0.5 text-slate-400 shrink-0" />
                      <a href={`https://doi.org/${publication.doi}`} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all">
                        {publication.doi}
                      </a>
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
          
          <PublicationReferences publicationId={publication.id} readOnly={true} />
        </div>

        <div className="space-y-6">
          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="bg-slate-50/50 border-b border-slate-100">
              <CardTitle className="text-lg">Document Access</CardTitle>
            </CardHeader>
            <CardContent className="p-6 flex flex-col gap-3">
              <Button 
                onClick={() => downloadPdf(publication.id)} 
                disabled={isDownloading}
                className="w-full bg-emerald-600 hover:bg-emerald-700"
              >
                <Download className="w-4 h-4 mr-2" />
                {isDownloading ? "Processing..." : "Download PDF"}
              </Button>
              
              {publication.url && (
                <Button variant="outline" asChild className="w-full">
                  <a href={publication.url} target="_blank" rel="noopener noreferrer">
                    <LinkIcon className="w-4 h-4 mr-2" />
                    Direct Link
                  </a>
                </Button>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
