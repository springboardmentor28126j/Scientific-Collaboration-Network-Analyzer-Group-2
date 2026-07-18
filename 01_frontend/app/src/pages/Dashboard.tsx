import { useAuthStore, useIsSuperAdmin, useIsInstitutionAdmin, useIsResearcher, useIsReviewer } from "@/stores/authStore";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Building2, Users, BookOpen, ClipboardCheck, Shield, Activity, PieChart as PieChartIcon } from "lucide-react";
import { useInstitutions } from "@/hooks/useAuthQuery";
import { useDashboard } from "@/hooks/useDashboardQuery";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";

export default function Dashboard() {
  const user = useAuthStore((state) => state.user);
  const isSuperAdmin = useIsSuperAdmin();
  const isInstitutionAdmin = useIsInstitutionAdmin();
  const isResearcher = useIsResearcher();
  const isReviewer = useIsReviewer();

  const { data: institutions } = useInstitutions();
  const { data: dashboard, isLoading } = useDashboard();

  const activeInstitutions = institutions?.filter((i) => i.is_active).length || 0;

  const STATUS_COLORS = {
    "Draft": "#94a3b8", // slate-400
    "Submitted": "#60a5fa", // blue-400
    "Under Review": "#f59e0b", // amber-500
    "Revision Required": "#f97316", // orange-500
    "Accepted": "#10b981", // emerald-500
    "Rejected": "#ef4444", // red-500
    "Published": "#a855f7", // purple-500
    "Archived": "#64748b" // slate-500
  };

  const chartData = dashboard?.publication_status ? [
    { name: "Draft", value: dashboard.publication_status.draft },
    { name: "Submitted", value: dashboard.publication_status.submitted },
    { name: "Under Review", value: dashboard.publication_status.under_review },
    { name: "Revision Required", value: dashboard.publication_status.revision_required },
    { name: "Accepted", value: dashboard.publication_status.accepted },
    { name: "Rejected", value: dashboard.publication_status.rejected },
    { name: "Published", value: dashboard.publication_status.published },
    { name: "Archived", value: dashboard.publication_status.archived },
  ].filter(item => item.value > 0) : [];

  if (isLoading) {
    return <div className="p-8 text-center text-slate-500">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Welcome, {user?.full_name?.split(" ")[0] || "User"}
        </h1>
        <p className="text-slate-500 mt-1">
          Here&apos;s what&apos;s happening in your research management system
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {isSuperAdmin && dashboard && (
          <>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Publications</CardDescription>
                <CardTitle className="text-3xl font-bold">{dashboard.total_publications || 0}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <BookOpen className="h-4 w-4" />
                  <span>Across platform</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Institutions</CardDescription>
                <CardTitle className="text-3xl font-bold">{dashboard.total_institutions || 0}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-sm text-emerald-600">
                  <Building2 className="h-4 w-4" />
                  <span>{activeInstitutions} active</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Researchers</CardDescription>
                <CardTitle className="text-3xl font-bold flex items-center gap-2">{dashboard.total_researchers || 0}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <Users className="h-4 w-4" />
                  <span>Registered researchers</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Reviewers</CardDescription>
                <CardTitle className="text-3xl font-bold flex items-center gap-2">{dashboard.total_reviewers || 0}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <ClipboardCheck className="h-4 w-4" />
                  <span>Registered reviewers</span>
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {isInstitutionAdmin && dashboard && (
          <>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Publications</CardDescription>
                <CardTitle className="text-3xl font-bold">{dashboard.total_publications || 0}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-sm text-emerald-600">
                  <BookOpen className="h-4 w-4" />
                  <span>By institution</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Researchers</CardDescription>
                <CardTitle className="text-3xl font-bold">{dashboard.total_researchers || 0}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <Users className="h-4 w-4" />
                  <span>Institution members</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Reviewers</CardDescription>
                <CardTitle className="text-3xl font-bold">{dashboard.total_reviewers || 0}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <ClipboardCheck className="h-4 w-4" />
                  <span>Institution reviewers</span>
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {isResearcher && dashboard && (
          <>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>My Publications</CardDescription>
                <CardTitle className="text-3xl font-bold flex items-center gap-2">
                  <BookOpen className="h-6 w-6 text-emerald-600" />
                  {dashboard.my_publications || 0}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-500">Primary author</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Co-authored</CardDescription>
                <CardTitle className="text-3xl font-bold flex items-center gap-2">
                  <Users className="h-6 w-6 text-blue-600" />
                  {dashboard.coauthored_publications || 0}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-500">Collaborator</p>
              </CardContent>
            </Card>
          </>
        )}

        {isReviewer && dashboard && (
          <>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Pending Reviews</CardDescription>
                <CardTitle className="text-3xl font-bold flex items-center gap-2">
                  <ClipboardCheck className="h-6 w-6 text-amber-500" />
                  {dashboard.pending_reviews || 0}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-500">Action required</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Completed Reviews</CardDescription>
                <CardTitle className="text-3xl font-bold flex items-center gap-2">
                  <Shield className="h-6 w-6 text-emerald-500" />
                  {dashboard.completed_reviews || 0}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-500">Past work</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Assigned</CardDescription>
                <CardTitle className="text-3xl font-bold flex items-center gap-2">
                  <Activity className="h-6 w-6 text-blue-500" />
                  {dashboard.assigned_reviews || 0}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-500">All assignments</p>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Publication Status Charts */}
      {(isSuperAdmin || isInstitutionAdmin || isResearcher) && chartData.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChartIcon className="h-5 w-5 text-slate-500" />
                Publication Status Distribution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.name as keyof typeof STATUS_COLORS]} />
                      ))}
                    </Pie>
                    <RechartsTooltip 
                      formatter={(value: number) => [`${value} Publications`, 'Count']}
                      contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Status Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis 
                      dataKey="name" 
                      tick={{ fontSize: 12 }} 
                      tickLine={false}
                      axisLine={{ stroke: '#e2e8f0' }}
                    />
                    <YAxis 
                      allowDecimals={false} 
                      tick={{ fontSize: 12 }} 
                      tickLine={false}
                      axisLine={false}
                    />
                    <RechartsTooltip 
                      formatter={(value: number) => [`${value} Publications`, 'Count']}
                      cursor={{ fill: '#f1f5f9' }}
                      contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.name as keyof typeof STATUS_COLORS]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Role-specific info */}
      <Card>
        <CardHeader>
          <CardTitle>
            {isSuperAdmin && "Super Admin Overview"}
            {isInstitutionAdmin && "Institution Admin Overview"}
            {isResearcher && "Researcher Dashboard"}
            {isReviewer && "Reviewer Dashboard"}
          </CardTitle>
          <CardDescription>
            {isSuperAdmin && "Manage all institutions on the platform. Activate or deactivate institutions as needed."}
            {isInstitutionAdmin && "Manage researchers and reviewers under your institution. Invite new team members."}
            {isResearcher && "Submit research papers, track submissions, and collaborate with reviewers."}
            {isReviewer && "Review assigned papers, provide feedback, and track your review history."}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
            <h3 className="font-medium text-slate-900 dark:text-white mb-2">Quick Tips</h3>
            <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
              {isSuperAdmin && (
                <>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 mt-0.5">•</span>
                    Use the Institutions page to view and manage all registered institutions
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 mt-0.5">•</span>
                    Deactivating an institution will lock out all its users immediately
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 mt-0.5">•</span>
                    Only verified institutions should be activated
                  </li>
                </>
              )}
              {isInstitutionAdmin && (
                <>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 mt-0.5">•</span>
                    Use the Users page to manage researchers and reviewers
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 mt-0.5">•</span>
                    New users will receive an email invite to set their password
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 mt-0.5">•</span>
                    Deactivated users cannot access the system until reactivated
                  </li>
                </>
              )}
              {(isResearcher || isReviewer) && (
                <>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 mt-0.5">•</span>
                    Your account is managed by your institution admin
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 mt-0.5">•</span>
                    Use the navigation menu to access your features
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 mt-0.5">•</span>
                    Contact your institution admin if you need assistance
                  </li>
                </>
              )}
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
