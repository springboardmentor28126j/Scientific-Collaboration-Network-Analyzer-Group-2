import { useAuthStore, useIsSuperAdmin, useIsInstitutionAdmin, useIsResearcher, useIsReviewer } from "@/stores/authStore";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Building2, Users, BookOpen, ClipboardCheck, Shield, Activity } from "lucide-react";
import { useInstitutions } from "@/hooks/useAuthQuery";
import { useInstitutionUsers } from "@/hooks/useAuthQuery";

export default function Dashboard() {
  const user = useAuthStore((state) => state.user);
  const isSuperAdmin = useIsSuperAdmin();
  const isInstitutionAdmin = useIsInstitutionAdmin();
  const isResearcher = useIsResearcher();
  const isReviewer = useIsReviewer();

  const { data: institutions } = useInstitutions({ enabled: isSuperAdmin });
  const { data: users } = useInstitutionUsers(undefined, { enabled: isInstitutionAdmin });

  const activeInstitutions = institutions?.filter((i) => i.is_active).length || 0;
  const totalInstitutions = institutions?.length || 0;
  const totalUsers = users?.length || 0;
  const activeUsers = users?.filter((u) => u.is_active).length || 0;

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
        {isSuperAdmin && (
          <>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Institutions</CardDescription>
                <CardTitle className="text-3xl font-bold">{totalInstitutions}</CardTitle>
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
                <CardDescription>Platform Status</CardDescription>
                <CardTitle className="text-3xl font-bold flex items-center gap-2">
                  <Shield className="h-6 w-6 text-amber-500" />
                  Active
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <Activity className="h-4 w-4" />
                  <span>Super Admin Access</span>
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {isInstitutionAdmin && (
          <>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Users</CardDescription>
                <CardTitle className="text-3xl font-bold">{totalUsers}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-sm text-emerald-600">
                  <Users className="h-4 w-4" />
                  <span>{activeUsers} active</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Institution</CardDescription>
                <CardTitle className="text-lg font-bold truncate">{user?.institution_id?.slice(0, 8) || "N/A"}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <Building2 className="h-4 w-4" />
                  <span>Admin Access</span>
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {isResearcher && (
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>My Research</CardDescription>
              <CardTitle className="text-3xl font-bold flex items-center gap-2">
                <BookOpen className="h-6 w-6 text-emerald-600" />
                Active
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-500">
                You can submit and manage your research papers here
              </p>
            </CardContent>
          </Card>
        )}

        {isReviewer && (
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Pending Reviews</CardDescription>
              <CardTitle className="text-3xl font-bold flex items-center gap-2">
                <ClipboardCheck className="h-6 w-6 text-blue-600" />
                Active
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-500">
                Review assigned research papers
              </p>
            </CardContent>
          </Card>
        )}
      </div>

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
