import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BookOpen, CalendarDays, FolderKanban, Handshake, Link2, Plus, Trash2, Upload } from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "@/api/client";
import { useAuthStore, useIsInstitutionAdmin } from "@/stores/authStore";

type Section = "publications" | "projects" | "conferences" | "collaborations" | "citations";

const sections: Array<{ key: Section; label: string; icon: typeof BookOpen }> = [
  { key: "publications", label: "Publications", icon: BookOpen },
  { key: "projects", label: "Projects", icon: FolderKanban },
  { key: "conferences", label: "Conferences", icon: CalendarDays },
  { key: "collaborations", label: "Collaborations", icon: Handshake },
  { key: "citations", label: "Citations", icon: Link2 },
];

export default function ResearchHub() {
  const [section, setSection] = useState<Section>("publications");
  const [showForm, setShowForm] = useState(false);
  const [publicationQuery, setPublicationQuery] = useState("");
  const [publicationStatus, setPublicationStatus] = useState("");
  const queryClient = useQueryClient();
  const user = useAuthStore((state) => state.user);
  const isAdmin = useIsInstitutionAdmin();
  const publications = useQuery({ queryKey: ["publications", publicationQuery, publicationStatus], queryFn: () => apiClient.listPublications({ query: publicationQuery || undefined, publication_status: publicationStatus || undefined }) });
  const projects = useQuery({ queryKey: ["projects"], queryFn: () => apiClient.listProjects() });
  const conferences = useQuery({ queryKey: ["conferences"], queryFn: () => apiClient.listConferences() });
  const collaborations = useQuery({ queryKey: ["collaborations"], queryFn: () => apiClient.listCollaborations() });
  const citations = useQuery({ queryKey: ["citations"], queryFn: () => apiClient.listCitations() });
  const canCreate = section === "publications" || section === "citations" ? user?.role !== "REVIEWER" : isAdmin;
  const refresh = () => { void queryClient.invalidateQueries({ queryKey: [section] }); void queryClient.invalidateQueries({ queryKey: ["research-dashboard"] }); };
  const create = useMutation({
    mutationFn: async (form: HTMLFormElement) => {
      const values = new FormData(form);
      if (section === "publications") {
        const record = await apiClient.createPublication({ title: String(values.get("title")), abstract: String(values.get("abstract") || "") || null, publication_type: String(values.get("publication_type")), status: String(values.get("status")), doi: String(values.get("doi") || "") || null, author_ids: user ? [user.id] : [] });
        const file = values.get("file");
        if (file instanceof File && file.size) await apiClient.uploadPublicationFile(record.id, file);
        return;
      }
      if (section === "projects") return apiClient.createProject({ name: String(values.get("name")), description: String(values.get("description") || "") || null, status: String(values.get("status")) });
      if (section === "conferences") return apiClient.createConference({ name: String(values.get("name")), location: String(values.get("location") || "") || null, starts_on: String(values.get("starts_on")) });
      if (section === "collaborations") return apiClient.createCollaboration({ partner_name: String(values.get("partner_name")), description: String(values.get("description") || "") || null, status: String(values.get("status")) });
      return apiClient.createCitation({ source_publication_id: String(values.get("source_publication_id")), cited_publication_id: String(values.get("cited_publication_id")) });
    },
    onSuccess: () => { refresh(); setShowForm(false); toast.success("Saved successfully"); },
    onError: (error: Error) => toast.error(error.message),
  });
  const remove = useMutation({
    mutationFn: (id: string) => {
      if (section === "publications") return apiClient.deletePublication(id);
      if (section === "projects") return apiClient.deleteProject(id);
      if (section === "conferences") return apiClient.deleteConference(id);
      if (section === "collaborations") return apiClient.deleteCollaboration(id);
      return apiClient.deleteCitation(id);
    },
    onSuccess: () => { refresh(); toast.success("Deleted successfully"); },
    onError: (error: Error) => toast.error(error.message),
  });
  const publish = useMutation({ mutationFn: (id: string) => apiClient.updatePublication(id, { status: "PUBLISHED" }), onSuccess: refresh, onError: (error: Error) => toast.error(error.message) });
  const current = sections.find((item) => item.key === section)!;

  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); create.mutate(event.currentTarget); }

  return <div className="space-y-7">
    <section className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between"><div><p className="page-eyebrow">Research workspace</p><h1 className="page-title">Research activity</h1><p className="mt-2 text-slate-500">Manage institutional research records, contributors, and activity.</p></div>{canCreate && <button onClick={() => setShowForm((visible) => !visible)} className="inline-flex items-center justify-center gap-2 rounded-xl bg-teal-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-teal-700"><Plus className="h-4 w-4" />Add {current.label.slice(0, -1)}</button>}</section>
    <section className="flex flex-wrap gap-2 border-b border-slate-200 pb-4">{sections.map(({ key, label, icon: Icon }) => <button key={key} onClick={() => { setSection(key); setShowForm(false); }} className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium ${section === key ? "bg-teal-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`}><Icon className="h-4 w-4" />{label}</button>)}</section>
    {section === "publications" && <section className="flex flex-wrap gap-3"><input value={publicationQuery} onChange={(event) => setPublicationQuery(event.target.value)} placeholder="Search title, abstract, or DOI" className="min-w-64 rounded-xl border border-slate-200 px-3 py-2 text-sm" /><select value={publicationStatus} onChange={(event) => setPublicationStatus(event.target.value)} className="rounded-xl border border-slate-200 px-3 py-2 text-sm"><option value="">All statuses</option><option>DRAFT</option><option>SUBMITTED</option><option>PUBLISHED</option><option>ARCHIVED</option></select></section>}
    {showForm && <form onSubmit={submit} className="surface-card grid gap-4 rounded-2xl p-5 md:grid-cols-2"><ResearchForm section={section} publications={publications.data ?? []} /><div className="md:col-span-2 flex justify-end gap-3"><button type="button" onClick={() => setShowForm(false)} className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold">Cancel</button><button disabled={create.isPending} className="rounded-xl bg-teal-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">{create.isPending ? "Saving…" : "Save"}</button></div></form>}
    <section className="surface-card overflow-hidden rounded-2xl"><RecordList section={section} isAdmin={isAdmin} publications={publications.data ?? []} projects={projects.data ?? []} conferences={conferences.data ?? []} collaborations={collaborations.data ?? []} citations={citations.data ?? []} onDelete={(id) => remove.mutate(id)} onPublish={(id) => publish.mutate(id)} /></section>
  </div>;
}

function ResearchForm({ section, publications }: { section: Section; publications: Array<{ id: string; title: string }> }) {
  if (section === "publications") return <><Field name="title" label="Title" required /><Field name="doi" label="DOI" /><textarea name="abstract" placeholder="Abstract" className="min-h-24 rounded-xl border border-slate-200 p-3 text-sm md:col-span-2" /><select name="publication_type" defaultValue="JOURNAL" className="rounded-xl border border-slate-200 p-3 text-sm"><option>JOURNAL</option><option>CONFERENCE</option><option>BOOK</option><option>PATENT</option><option>TECHNICAL_REPORT</option></select><select name="status" defaultValue="DRAFT" className="rounded-xl border border-slate-200 p-3 text-sm"><option>DRAFT</option><option>SUBMITTED</option><option>PUBLISHED</option><option>ARCHIVED</option></select><label className="inline-flex items-center gap-2 text-sm text-slate-600 md:col-span-2"><Upload className="h-4 w-4" />PDF attachment <input name="file" type="file" accept="application/pdf,.pdf" /></label></>;
  if (section === "projects") return <><Field name="name" label="Project name" required /><select name="status" defaultValue="ACTIVE" className="rounded-xl border border-slate-200 p-3 text-sm"><option>ACTIVE</option><option>ON_HOLD</option><option>COMPLETED</option></select><textarea name="description" placeholder="Project description" className="min-h-24 rounded-xl border border-slate-200 p-3 text-sm md:col-span-2" /></>;
  if (section === "conferences") return <><Field name="name" label="Conference name" required /><Field name="location" label="Location" /><label className="text-sm font-medium text-slate-700">Start date<input name="starts_on" type="date" required className="mt-1 block w-full rounded-xl border border-slate-200 p-3 font-normal" /></label></>;
  if (section === "collaborations") return <><Field name="partner_name" label="Partner institution or organization" required /><select name="status" defaultValue="ACTIVE" className="rounded-xl border border-slate-200 p-3 text-sm"><option>ACTIVE</option><option>PAUSED</option><option>COMPLETED</option></select><textarea name="description" placeholder="Collaboration description" className="min-h-24 rounded-xl border border-slate-200 p-3 text-sm md:col-span-2" /></>;
  return <><label className="text-sm font-medium text-slate-700">Source publication<select name="source_publication_id" required className="mt-1 block w-full rounded-xl border border-slate-200 p-3 font-normal"><option value="">Select a publication</option>{publications.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label><label className="text-sm font-medium text-slate-700">Cited publication<select name="cited_publication_id" required className="mt-1 block w-full rounded-xl border border-slate-200 p-3 font-normal"><option value="">Select a publication</option>{publications.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label></>;
}

function Field({ name, label, required = false }: { name: string; label: string; required?: boolean }) { return <label className="text-sm font-medium text-slate-700">{label}<input name={name} required={required} className="mt-1 block w-full rounded-xl border border-slate-200 p-3 font-normal" /></label>; }

function RecordList({ section, isAdmin, publications, projects, conferences, collaborations, citations, onDelete, onPublish }: { section: Section; isAdmin: boolean; publications: Array<{ id: string; title: string; status: string; publication_type: string; doi: string | null; file_url: string | null }>; projects: Array<{ id: string; name: string; status: string; member_ids: string[] }>; conferences: Array<{ id: string; name: string; location: string | null; starts_on: string }>; collaborations: Array<{ id: string; partner_name: string; status: string; description: string | null }>; citations: Array<{ id: string; source_publication_id: string; cited_publication_id: string }>; onDelete: (id: string) => void; onPublish: (id: string) => void }) {
  const deletable = section !== "publications" || isAdmin;
  const empty = <p className="p-10 text-center text-sm text-slate-500">No {section} have been recorded yet.</p>;
  if (section === "publications") return publications.length ? <div>{publications.map((item) => <article key={item.id} className="flex flex-wrap items-center gap-4 border-b border-slate-100 p-5 last:border-0"><div className="min-w-0 flex-1"><h2 className="font-semibold text-slate-950">{item.title}</h2><p className="mt-1 text-sm text-slate-500">{item.publication_type} · {item.status}{item.doi ? ` · DOI: ${item.doi}` : ""}</p>{item.file_url && <a href={item.file_url} target="_blank" rel="noreferrer" className="mt-2 inline-block text-sm font-medium text-teal-700">View attachment</a>}</div>{item.status !== "PUBLISHED" && <button onClick={() => onPublish(item.id)} className="rounded-lg border border-teal-200 px-3 py-2 text-xs font-semibold text-teal-700">Mark published</button>}{deletable && <DeleteButton onClick={() => onDelete(item.id)} />}</article>)}</div> : empty;
  if (section === "projects") return projects.length ? <div>{projects.map((item) => <Row key={item.id} title={item.name} detail={`${item.status} · ${item.member_ids.length} assigned member(s)`} deletable={deletable} onDelete={() => onDelete(item.id)} />)}</div> : empty;
  if (section === "conferences") return conferences.length ? <div>{conferences.map((item) => <Row key={item.id} title={item.name} detail={`${item.location || "Location pending"} · ${new Date(item.starts_on).toLocaleDateString()}`} deletable={deletable} onDelete={() => onDelete(item.id)} />)}</div> : empty;
  if (section === "collaborations") return collaborations.length ? <div>{collaborations.map((item) => <Row key={item.id} title={item.partner_name} detail={`${item.status}${item.description ? ` · ${item.description}` : ""}`} deletable={deletable} onDelete={() => onDelete(item.id)} />)}</div> : empty;
  return citations.length ? <div>{citations.map((item) => <Row key={item.id} title="Publication citation" detail={`${item.source_publication_id} → ${item.cited_publication_id}`} deletable onDelete={() => onDelete(item.id)} />)}</div> : empty;
}

function Row({ title, detail, deletable, onDelete }: { title: string; detail: string; deletable: boolean; onDelete: () => void }) { return <article className="flex items-center gap-4 border-b border-slate-100 p-5 last:border-0"><div className="min-w-0 flex-1"><h2 className="font-semibold text-slate-950">{title}</h2><p className="mt-1 truncate text-sm text-slate-500">{detail}</p></div>{deletable && <DeleteButton onClick={onDelete} />}</article>; }
function DeleteButton({ onClick }: { onClick: () => void }) { return <button onClick={onClick} className="rounded-lg p-2 text-rose-600 hover:bg-rose-50" aria-label="Delete"><Trash2 className="h-4 w-4" /></button>; }
