import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { FileDown, FileSpreadsheet, FileText } from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "@/api/client";

export default function Reports() {
  const [downloading, setDownloading] = useState<"pdf" | "xlsx" | null>(null);
  const publication = useQuery({ queryKey: ["report-publication"], queryFn: () => apiClient.getReport("summary") });
  const research = useQuery({ queryKey: ["report-research"], queryFn: () => apiClient.getReport("research") });
  const collaboration = useQuery({ queryKey: ["report-collaboration"], queryFn: () => apiClient.getReport("collaborations") });
  const institution = useQuery({ queryKey: ["report-institution"], queryFn: () => apiClient.getReport("institution") });

  async function download(format: "pdf" | "xlsx") {
    setDownloading(format);
    try {
      const blob = await apiClient.downloadReport(format);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `publications.${format}`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Unable to generate report");
    } finally {
      setDownloading(null);
    }
  }

  return <div className="space-y-7">
    <section><p className="page-eyebrow">Research reports</p><h1 className="page-title">Export publication data</h1><p className="mt-2 text-slate-500">Download your institution's publication register in a shareable format.</p></section>
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <ReportCard title="Publication Report" values={publication.data} />
      <ReportCard title="Research Report" values={research.data} />
      <ReportCard title="Collaboration Report" values={collaboration.data} />
      <ReportCard title="Institution Report" values={institution.data} />
    </section>
    <section className="grid gap-5 md:grid-cols-2">
      <button onClick={() => void download("pdf")} disabled={downloading !== null} className="surface-card rounded-2xl p-6 text-left transition hover:border-teal-300 hover:shadow-md disabled:opacity-60"><FileText className="h-8 w-8 text-rose-600" /><h2 className="mt-5 text-lg font-semibold">PDF report</h2><p className="mt-2 text-sm text-slate-500">A formatted publication report ready to share or print.</p><span className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-teal-700"><FileDown className="h-4 w-4" />{downloading === "pdf" ? "Preparing…" : "Download PDF"}</span></button>
      <button onClick={() => void download("xlsx")} disabled={downloading !== null} className="surface-card rounded-2xl p-6 text-left transition hover:border-teal-300 hover:shadow-md disabled:opacity-60"><FileSpreadsheet className="h-8 w-8 text-emerald-600" /><h2 className="mt-5 text-lg font-semibold">Excel workbook</h2><p className="mt-2 text-sm text-slate-500">A spreadsheet containing all publication metadata and DOI values.</p><span className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-teal-700"><FileDown className="h-4 w-4" />{downloading === "xlsx" ? "Preparing…" : "Download Excel"}</span></button>
    </section>
  </div>;
}

function ReportCard({ title, values }: { title: string; values?: Record<string, number> }) { return <div className="surface-card rounded-2xl p-5"><h2 className="font-semibold text-slate-950">{title}</h2><div className="mt-4 space-y-2 text-sm text-slate-500">{values ? Object.entries(values).map(([key, value]) => <p key={key} className="flex justify-between"><span className="capitalize">{key.replaceAll("_", " ")}</span><b className="text-slate-900">{value}</b></p>) : <p>Loading…</p>}</div></div>; }
