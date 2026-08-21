import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { UserMinus, UserPlus, Users } from "lucide-react";
import { apiClient } from "@/api/client";

export default function Coauthors() {
  const client = useQueryClient();
  const [publicationId, setPublicationId] = useState("");
  const [authorId, setAuthorId] = useState("");
  const publications = useQuery({ queryKey: ["publications"], queryFn: () => apiClient.listPublications() });
  const publication = publications.data?.find((item) => item.id === publicationId);
  const update = useMutation({ mutationFn: (author_ids: string[]) => apiClient.updatePublication(publicationId, { author_ids }), onSuccess: () => void client.invalidateQueries({ queryKey: ["publications"] }) });
  const authors = publication?.author_ids || [];
  return <div className="space-y-6"><div><p className="page-eyebrow">Publication contributors</p><h1 className="page-title">Co-authors</h1><p className="mt-2 text-slate-500">Manage the contributors linked to each publication.</p></div><select value={publicationId} onChange={(event) => setPublicationId(event.target.value)} className="w-full max-w-xl rounded-xl border p-3"><option value="">Select publication</option>{publications.data?.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select>{publication && <section className="surface-card rounded-2xl p-5"><h2 className="font-semibold">{publication.title}</h2><form onSubmit={(event) => { event.preventDefault(); if (authorId && !authors.includes(authorId)) { update.mutate([...authors, authorId]); setAuthorId(""); } }} className="mt-4 flex gap-2"><input value={authorId} onChange={(event) => setAuthorId(event.target.value)} placeholder="Researcher user ID" className="flex-1 rounded-xl border p-3" /><button className="rounded-xl bg-teal-600 px-4 text-white"><UserPlus className="inline h-4 w-4" /> Add Co-author</button></form><div className="mt-5 space-y-2">{authors.length ? authors.map((id) => <div key={id} className="flex items-center justify-between rounded-xl bg-slate-50 p-3 text-sm"><span><Users className="mr-2 inline h-4 w-4 text-teal-600" />{id}</span><button onClick={() => update.mutate(authors.filter((author) => author !== id))} className="text-rose-600"><UserMinus className="inline h-4 w-4" /> Remove</button></div>) : <p className="text-sm text-slate-500">No co-authors assigned.</p>}</div></section>}</div>;
}
