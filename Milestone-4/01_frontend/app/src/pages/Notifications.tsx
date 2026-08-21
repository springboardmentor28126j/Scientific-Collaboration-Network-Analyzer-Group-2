import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, CheckCheck } from "lucide-react";
import { apiClient } from "@/api/client";

export default function Notifications() {
  const queryClient = useQueryClient();
  const notifications = useQuery({ queryKey: ["notifications"], queryFn: () => apiClient.listNotifications() });
  const markRead = useMutation({ mutationFn: (id: string) => apiClient.markNotificationRead(id), onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["notifications"] }) });

  return <div className="space-y-7"><section><p className="page-eyebrow">Activity</p><h1 className="page-title">Notifications</h1><p className="mt-2 text-slate-500">Publication changes and project assignments for your account.</p></section><section className="surface-card overflow-hidden rounded-2xl">{notifications.isLoading ? <p className="p-6 text-sm text-slate-500">Loading notifications…</p> : !notifications.data?.length ? <div className="p-12 text-center text-slate-500"><Bell className="mx-auto mb-3 h-8 w-8 text-slate-300" />You are all caught up.</div> : notifications.data.map((notification) => <article key={notification.id} className={`flex gap-4 border-b border-slate-100 p-5 last:border-0 ${notification.is_read ? "" : "bg-teal-50/50"}`}><Bell className="mt-0.5 h-5 w-5 shrink-0 text-teal-600" /><div className="min-w-0 flex-1"><h2 className="font-semibold text-slate-900">{notification.title}</h2><p className="mt-1 text-sm text-slate-600">{notification.message}</p><p className="mt-2 text-xs text-slate-400">{new Date(notification.created_at).toLocaleString()}</p></div>{!notification.is_read && <button onClick={() => markRead.mutate(notification.id)} className="inline-flex h-9 items-center gap-1 rounded-lg border border-teal-200 px-3 text-xs font-semibold text-teal-700"><CheckCheck className="h-4 w-4" />Read</button>}</article>)}</section></div>;
}
