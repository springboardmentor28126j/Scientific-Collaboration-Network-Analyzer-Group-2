import { useQuery } from "@tanstack/react-query";
import { Users } from "lucide-react";
import { apiClient } from "@/api/client";

export default function GlobalResearchers() {
  const researchers = useQuery({ queryKey: ["global-researchers"], queryFn: () => apiClient.listGlobalResearchers() });
  return <div className="space-y-6"><div><p className="page-eyebrow">Platform directory</p><h1 className="page-title">Researchers</h1><p className="mt-2 text-slate-500">All researchers registered across institutions.</p></div><section className="surface-card overflow-hidden rounded-2xl">{researchers.isLoading ? <p className="p-6 text-sm text-slate-500">Loading researchers…</p> : !researchers.data?.length ? <div className="p-12 text-center text-slate-500"><Users className="mx-auto mb-3 h-8 w-8 text-slate-300" />No researchers have been added yet.</div> : researchers.data.map((researcher) => <article key={researcher.id} className="flex items-center gap-4 border-b border-slate-100 p-5 last:border-0"><div className="grid h-10 w-10 place-items-center rounded-full bg-teal-100 font-semibold text-teal-700">{researcher.full_name.charAt(0)}</div><div><h2 className="font-semibold text-slate-950">{researcher.full_name}</h2><p className="text-sm text-slate-500">{researcher.email} · {researcher.institution_name || "No institution"}</p></div></article>)}</section></div>;
}
