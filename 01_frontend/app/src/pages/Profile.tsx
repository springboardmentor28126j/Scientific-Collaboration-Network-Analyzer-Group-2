import { useAuthStore } from "@/stores/authStore";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { UserCircle, Mail, Shield, Building2, Calendar, CheckCircle2, XCircle } from "lucide-react";

export default function Profile() {
  const user = useAuthStore((state) => state.user);

  if (!user) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-slate-500">Loading profile...</p>
      </div>
    );
  }

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case "SUPER_ADMIN":
        return "bg-amber-100 text-amber-700 border-amber-200";
      case "INSTITUTION_ADMIN":
        return "bg-blue-100 text-blue-700 border-blue-200";
      case "RESEARCHER":
        return "bg-emerald-100 text-emerald-700 border-emerald-200";
      case "REVIEWER":
        return "bg-purple-100 text-purple-700 border-purple-200";
      default:
        return "bg-slate-100 text-slate-700";
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <UserCircle className="h-6 w-6" />
          Profile
        </h1>
        <p className="text-slate-500 mt-1">
          Your account information
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Avatar & Basic Info */}
        <Card className="lg:col-span-1">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="w-24 h-24 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl font-bold text-emerald-700">
                  {user.full_name.charAt(0).toUpperCase()}
                </span>
              </div>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                {user.full_name}
              </h2>
              <Badge
                variant="outline"
                className={`mt-2 capitalize ${getRoleBadgeColor(user.role)}`}
              >
                {user.role.toLowerCase().replace("_", " ")}
              </Badge>
              <div className="mt-4 flex items-center justify-center gap-1 text-sm">
                {user.is_active ? (
                  <>
                    <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                    <span className="text-emerald-600">Active</span>
                  </>
                ) : (
                  <>
                    <XCircle className="h-4 w-4 text-red-600" />
                    <span className="text-red-600">Inactive</span>
                  </>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Detailed Info */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Account Details</CardTitle>
            <CardDescription>
              Detailed information about your account
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800">
                <Mail className="h-5 w-5 text-slate-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-slate-900 dark:text-white">Email</p>
                  <p className="text-sm text-slate-500">{user.email}</p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800">
                <Shield className="h-5 w-5 text-slate-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-slate-900 dark:text-white">Role</p>
                  <p className="text-sm text-slate-500 capitalize">
                    {user.role.toLowerCase().replace("_", " ")}
                  </p>
                </div>
              </div>

              {user.institution_id && (
                <div className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800">
                  <Building2 className="h-5 w-5 text-slate-400 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-slate-900 dark:text-white">
                      Institution
                    </p>
                    <p className="text-sm text-slate-500 font-mono">{user.institution_id}</p>
                  </div>
                </div>
              )}

              <div className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800">
                <Calendar className="h-5 w-5 text-slate-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-slate-900 dark:text-white">Joined</p>
                  <p className="text-sm text-slate-500">
                    {new Date(user.created_at).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}
                  </p>
                </div>
              </div>
            </div>

            {user.description && (
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800">
                <p className="text-sm font-medium text-slate-900 dark:text-white mb-1">
                  Description
                </p>
                <p className="text-sm text-slate-500">{user.description}</p>
              </div>
            )}

            <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800">
              <p className="text-sm font-medium text-slate-900 dark:text-white mb-1">
                Account Status
              </p>
              <div className="flex items-center gap-4 mt-2">
                <div className="flex items-center gap-2">
                  <div
                    className={`h-2.5 w-2.5 rounded-full ${
                      user.is_verified ? "bg-emerald-500" : "bg-amber-500"
                    }`}
                  />
                  <span className="text-sm text-slate-500">
                    {user.is_verified ? "Verified" : "Not Verified"}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div
                    className={`h-2.5 w-2.5 rounded-full ${
                      user.is_active ? "bg-emerald-500" : "bg-red-500"
                    }`}
                  />
                  <span className="text-sm text-slate-500">
                    {user.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
