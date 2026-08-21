import {
  useAuthStore,
  useIsInstitutionAdmin,
  useIsResearcher,
  useIsReviewer,
  useIsSuperAdmin,
} from "@/stores/authStore";
import { Card, CardContent } from "@/components/ui/card";
import {
  Activity,
  ArrowUpRight,
  BookOpen,
  Building2,
  CheckCircle2,
  ClipboardCheck,
  ShieldCheck,
  Users,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/api/client";
import { useInstitutionUsers, useInstitutions } from "@/hooks/useAuthQuery";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface StatCardProps {
  label: string;
  value: string | number;
  detail: string;
  icon: React.ReactNode;
  tone: string;
}

function StatCard({ label, value, detail, icon, tone }: StatCardProps) {
  return (
    <Card className="surface-card overflow-hidden border-0">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-slate-500">{label}</p>
            <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">{value}</p>
          </div>
          <div className={`grid h-10 w-10 place-items-center rounded-xl ${tone}`}>{icon}</div>
        </div>
        <p className="mt-5 flex items-center gap-1.5 text-sm text-slate-500">
          <ArrowUpRight className="h-4 w-4 text-teal-600" />
          {detail}
        </p>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const user = useAuthStore((state) => state.user);
  const isSuperAdmin = useIsSuperAdmin();
  const isInstitutionAdmin = useIsInstitutionAdmin();
  const isResearcher = useIsResearcher();
  const isReviewer = useIsReviewer();

  const { data: institutions } = useInstitutions({ enabled: isSuperAdmin });
  const { data: users } = useInstitutionUsers(undefined, { enabled: isInstitutionAdmin });
  const analytics = useQuery({
    queryKey: ["research-analytics"],
    queryFn: () => apiClient.getAnalytics(),
    enabled: !isSuperAdmin,
  });
  const activeInstitutions = institutions?.filter((institution) => institution.is_active).length ?? 0;
  const activeUsers = users?.filter((member) => member.is_active).length ?? 0;
  const firstName = user?.full_name?.split(" ")[0] || "there";

  const stats = isSuperAdmin
    ? [
        { label: "Institutions", value: institutions?.length ?? 0, detail: `${activeInstitutions} currently active`, icon: <Building2 className="h-5 w-5" />, tone: "bg-teal-50 text-teal-700" },
        { label: "Platform status", value: "Healthy", detail: "All services operational", icon: <Activity className="h-5 w-5" />, tone: "bg-sky-50 text-sky-700" },
        { label: "Access control", value: "Secure", detail: "Role permissions enabled", icon: <ShieldCheck className="h-5 w-5" />, tone: "bg-violet-50 text-violet-700" },
      ]
    : isInstitutionAdmin
      ? [
          { label: "Team members", value: users?.length ?? 0, detail: `${activeUsers} active accounts`, icon: <Users className="h-5 w-5" />, tone: "bg-teal-50 text-teal-700" },
          { label: "Researchers", value: users?.filter((member) => member.role === "RESEARCHER").length ?? 0, detail: "In your institution", icon: <BookOpen className="h-5 w-5" />, tone: "bg-sky-50 text-sky-700" },
          { label: "Reviewers", value: users?.filter((member) => member.role === "REVIEWER").length ?? 0, detail: "Available to review", icon: <ClipboardCheck className="h-5 w-5" />, tone: "bg-violet-50 text-violet-700" },
        ]
      : [
          { label: isResearcher ? "Research workspace" : "Review workspace", value: "Ready", detail: "Your account is active", icon: isResearcher ? <BookOpen className="h-5 w-5" /> : <ClipboardCheck className="h-5 w-5" />, tone: "bg-teal-50 text-teal-700" },
          { label: "Account status", value: "Active", detail: "Institution-managed access", icon: <CheckCircle2 className="h-5 w-5" />, tone: "bg-sky-50 text-sky-700" },
          { label: "Next step", value: isReviewer ? "Review" : "Submit", detail: isReviewer ? "Check assigned papers" : "Prepare your paper", icon: <ArrowUpRight className="h-5 w-5" />, tone: "bg-violet-50 text-violet-700" },
        ];

  const roleLabel = user?.role?.toLowerCase().replace("_", " ") || "member";

  return (
    <div className="space-y-8">
      <section className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
        <div>
          <p className="page-eyebrow">{roleLabel} workspace</p>
          <h1 className="page-title">Good to see you, {firstName}.</h1>
          <p className="mt-3 max-w-2xl text-base text-slate-500">A clear view of your research network, people, and next actions.</p>
        </div>
        <div className="rounded-xl border border-teal-100 bg-teal-50 px-4 py-3 text-sm text-teal-800">
          <span className="font-semibold">Workspace active</span>
          <span className="mx-2 text-teal-400">•</span>
          All systems running
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {stats.map((stat) => <StatCard key={stat.label} {...stat} />)}
      </section>

      {!isSuperAdmin && <AnalyticsPanel data={analytics.data} isLoading={analytics.isLoading} />}

      <section className="grid gap-6 lg:grid-cols-[1.55fr_1fr]">
        <Card className="surface-card border-0">
          <CardContent className="p-6 sm:p-7">
            <p className="page-eyebrow">Getting started</p>
            <h2 className="text-xl font-semibold text-slate-950">Make the most of ResearchMesh</h2>
            <div className="mt-6 space-y-4">
              {(isSuperAdmin
                ? ["Review new institution registrations before activating access.", "Use the institution directory to keep platform access current.", "Monitor platform health and permissions from this workspace."]
                : isInstitutionAdmin
                  ? ["Invite researchers and reviewers from the Users page.", "Keep account status current for uninterrupted access.", "Use roles to give each member the right workspace."]
                  : isReviewer
                    ? ["Open My Reviews to see papers assigned to you.", "Keep your profile details current for your institution.", "Contact your institution admin for access changes."]
                    : ["Open My Research to manage your future submissions.", "Keep your profile details current for your institution.", "Contact your institution admin for access changes."]
              ).map((tip, index) => (
                <div key={tip} className="flex gap-4 rounded-xl bg-slate-50 p-4">
                  <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-slate-950 text-xs font-semibold text-white">{index + 1}</span>
                  <p className="pt-0.5 text-sm leading-6 text-slate-600">{tip}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="overflow-hidden border-0 bg-[#102a35] text-white shadow-sm">
          <CardContent className="p-6 sm:p-7">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-teal-400 text-slate-950"><FlaskIcon /></div>
            <p className="mt-8 text-sm font-medium text-teal-300">ResearchMesh</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight">Your work, connected.</h2>
            <p className="mt-3 text-sm leading-6 text-slate-300">A focused environment for institutions, research teams, and peer reviewers.</p>
            <div className="mt-8 border-t border-slate-700 pt-5 text-sm text-slate-400">Signed in as <span className="font-medium text-white">{user?.email}</span></div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}

function FlaskIcon() {
  return <Activity className="h-5 w-5" />;
}

interface AnalyticsPanelProps {
  data?: any;
  isLoading: boolean;
}

function AnalyticsPanel({ data, isLoading }: AnalyticsPanelProps) {
  const cards = data?.cards ?? {};
  const publicationYears = data?.publications_per_year ?? [];
  const departments = data?.publications_by_department ?? [];
  const collaborationStats = data?.collaboration_statistics ?? [];
  const institutions = data?.institution_statistics ?? [];
  const activity = data?.recent_activity ?? [];
  const metrics = [
    ["Researchers", cards.researchers ?? 0, <Users className="h-5 w-5" />],
    ["Publications", cards.publications ?? 0, <BookOpen className="h-5 w-5" />],
    ["Conferences", cards.conferences ?? 0, <Activity className="h-5 w-5" />],
    ["Projects", cards.projects ?? 0, <ClipboardCheck className="h-5 w-5" />],
    ["Collaborations", cards.collaborations ?? 0, <Building2 className="h-5 w-5" />],
  ];

  return (
    <section className="space-y-6">
      <div>
        <p className="page-eyebrow">Live analytics</p>
        <h2 className="text-xl font-semibold text-slate-950">Research network overview</h2>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        {metrics.map(([label, value, icon]) => (
          <Card key={String(label)} className="surface-card border-0">
            <CardContent className="p-4">
              <div className="flex items-center justify-between text-teal-700">{icon}</div>
              <p className="mt-3 text-2xl font-semibold text-slate-950">{isLoading ? "–" : value}</p>
              <p className="mt-1 text-sm text-slate-500">{label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <AnalyticsChart title="Publications per year" data={publicationYears} dataKey="count" nameKey="year" />
        <AnalyticsChart title="Publications by department" data={departments} dataKey="count" nameKey="department" />
        <AnalyticsChart title="Collaboration statistics" data={collaborationStats} dataKey="value" nameKey="name" />
        <AnalyticsChart title="Institution statistics" data={institutions} dataKey="value" nameKey="name" />
      </div>

      <Card className="surface-card border-0">
        <CardContent className="p-6">
          <p className="page-eyebrow">Recent activity</p>
          <h2 className="text-xl font-semibold text-slate-950">Latest publications</h2>
          <div className="mt-5 space-y-3">
            {activity.length ? activity.map((item: any) => (
              <div key={item.id} className="flex items-center justify-between gap-4 rounded-xl bg-slate-50 px-4 py-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-slate-900">{item.title}</p>
                  <p className="mt-1 text-xs text-slate-500">{item.type}</p>
                </div>
                <span className="shrink-0 text-xs text-slate-400">{item.date ? new Date(item.date).toLocaleDateString() : ""}</span>
              </div>
            )) : <p className="py-4 text-sm text-slate-500">No publication activity yet.</p>}
          </div>
        </CardContent>
      </Card>
    </section>
  );
}

function AnalyticsChart({ title, data, dataKey, nameKey }: { title: string; data: any[]; dataKey: string; nameKey: string }) {
  return (
    <Card className="surface-card border-0">
      <CardContent className="p-6">
        <h3 className="font-semibold text-slate-950">{title}</h3>
        <div className="mt-5 h-64">
          {data.length ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey={nameKey} tickLine={false} axisLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />
                <YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />
                <Tooltip cursor={{ fill: "#f0fdfa" }} />
                <Bar dataKey={dataKey} fill="#14b8a6" radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <div className="grid h-full place-items-center rounded-xl bg-slate-50 text-sm text-slate-500">No data available yet.</div>}
        </div>
      </CardContent>
    </Card>
  );
}
