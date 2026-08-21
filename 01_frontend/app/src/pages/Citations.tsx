import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link2, Plus, Trash2 } from "lucide-react";
import { apiClient } from "@/api/client";

export default function Citations() {
  const client = useQueryClient();
  const [sourceId, setSourceId] = useState("");
  const [citedId, setCitedId] = useState("");
  const publications = useQuery({ queryKey: ["publications"], queryFn: () => apiClient.listPublications() });
  const citations = useQuery({ queryKey: ["citations"], queryFn: () => apiClient.listCitations() });
  const publicationName = (id: string) => publications.data?.find((publication) => publication.id === id)?.title || id;
  const publicationDoi = (id: string) => publications.data?.find((publication) => publication.id === id)?.doi || "No DOI";
  const create = useMutation({ mutationFn: () => apiClient.createCitation({ source_publication_id: sourceId, cited_publication_id: citedId }), onSuccess: () => { setSourceId(""); setCitedId(""); void client.invalidateQueries({ queryKey: ["citations"] }); } });
  const remove = useMutation({ mutationFn: apiClient.deleteCitation.bind(apiClient), onSuccess: () => void client.invalidateQueries({ queryKey: ["citations"] }) });
  return <div className="space-y-6"><div><p className="page-eyebrow">Publication references</p><h1 className="page-title">Citations</h1><p className="mt-2 text-slate-500">Link publications, manage citation records, and view DOI details.</p></div><section className="surface-card grid gap-3 rounded-2xl p-5 md:grid-cols-2"><select value={sourceId} onChange={(event) => setSourceId(event.target.value)} className="rounded-xl border p-3"><option value="">Source publication</option>{publications.data?.map((publication) => <option key={publication.id} value={publication.id}>{publication.title}</option>)}</select><select value={citedId} onChange={(event) => setCitedId(event.target.value)} className="rounded-xl border p-3"><option value="">Referenced publication</option>{publications.data?.map((publication) => <option key={publication.id} value={publication.id}>{publication.title}</option>)}</select><button disabled={!sourceId || !citedId || create.isPending} onClick={() => create.mutate()} className="rounded-xl bg-teal-600 px-4 py-3 text-white disabled:opacity-50 md:col-span-2"><Plus className="inline h-4 w-4" /> Add Citation Record</button></section><section className="surface-card overflow-hidden rounded-2xl"><h2 className="border-b p-5 font-semibold">Reference List</h2>{!citations.data?.length ? <p className="p-10 text-center text-slate-500">No citation records yet.</p> : citations.data.map((citation) => <article key={citation.id} className="flex items-start gap-3 border-b p-5"><Link2 className="mt-1 text-teal-600" /><div className="flex-1"><p className="font-medium">{publicationName(citation.source_publication_id)}</p><p className="mt-1 text-sm text-slate-500">references {publicationName(citation.cited_publication_id)}</p><p className="mt-2 text-xs text-slate-400">DOI: {publicationDoi(citation.cited_publication_id)}</p></div><button onClick={() => remove.mutate(citation.id)} className="p-2 text-rose-600"><Trash2 className="h-4 w-4" /></button></article>)}</section></div>;
}
