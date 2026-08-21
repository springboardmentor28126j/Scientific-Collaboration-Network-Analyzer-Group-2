import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/authStore";
import { apiClient } from "@/api/client";
import { toast } from "sonner";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { UserCircle, Mail, Shield, Building2, Calendar, CheckCircle2, XCircle } from "lucide-react";

export default function Profile() {
  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();
  const profile = useQuery({ queryKey: ["researcher-profile"], queryFn: () => apiClient.getResearcherProfile(), enabled: user?.role === "RESEARCHER" });
  const [editingAcademicProfile, setEditingAcademicProfile] = useState(false);
  const updateAcademicProfile = useMutation({ mutationFn: apiClient.updateResearcherProfile.bind(apiClient), onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ["researcher-profile"] }); setEditingAcademicProfile(false); toast.success("Academic profile updated"); }, onError: (error: Error) => toast.error(error.message) });

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
      {user.role === "RESEARCHER" && <Card>
        <CardHeader><CardTitle>Academic Profile</CardTitle><CardDescription>Manage your department, research expertise, and affiliations.</CardDescription></CardHeader>
        <CardContent>{profile.isLoading ? <p className="text-sm text-slate-500">Loading academic profile…</p> : editingAcademicProfile ? <AcademicProfileForm profile={profile.data} onCancel={() => setEditingAcademicProfile(false)} onSave={(data) => updateAcademicProfile.mutate(data)} saving={updateAcademicProfile.isPending} /> : <div className="space-y-4"><AcademicDetail label="Department" value={profile.data?.department || "Not provided"} /><AcademicDetail label="Skills" value={profile.data?.skills?.join(", ") || "Not provided"} /><AcademicDetail label="Research interests" value={profile.data?.research_interests?.join(", ") || "Not provided"} /><AcademicDetail label="Affiliations" value={profile.data?.affiliations?.join(", ") || "Not provided"} /><Button onClick={() => setEditingAcademicProfile(true)}>Edit academic profile</Button></div>}</CardContent>
      </Card>}
    </div>
  );
}

function AcademicDetail({ label, value }: { label: string; value: string }) { return <div className="rounded-lg bg-slate-50 p-3"><p className="text-sm font-medium text-slate-900">{label}</p><p className="mt-1 text-sm text-slate-500">{value}</p></div>; }

function AcademicProfileForm({ profile, onCancel, onSave, saving }: { profile?: { department: string | null; skills: string[]; research_interests: string[]; affiliations: string[] }; onCancel: () => void; onSave: (data: { department: string | null; skills: string[]; research_interests: string[]; affiliations: string[] }) => void; saving: boolean }) {
  const [department, setDepartment] = useState(profile?.department || "");
  const [skills, setSkills] = useState(profile?.skills?.join(", ") || "");
  const [interests, setInterests] = useState(profile?.research_interests?.join(", ") || "");
  const [affiliations, setAffiliations] = useState(profile?.affiliations?.join(", ") || "");
  const list = (value: string) => value.split(",").map((item) => item.trim()).filter(Boolean);
  return <form onSubmit={(event) => { event.preventDefault(); onSave({ department: department || null, skills: list(skills), research_interests: list(interests), affiliations: list(affiliations) }); }} className="grid gap-4 md:grid-cols-2"><label className="text-sm font-medium">Department<Input value={department} onChange={(event) => setDepartment(event.target.value)} className="mt-1" /></label><label className="text-sm font-medium">Skills<Input value={skills} onChange={(event) => setSkills(event.target.value)} className="mt-1" placeholder="Data analysis, Python" /></label><label className="text-sm font-medium">Research interests<Input value={interests} onChange={(event) => setInterests(event.target.value)} className="mt-1" placeholder="Machine learning, health" /></label><label className="text-sm font-medium">Affiliations<Input value={affiliations} onChange={(event) => setAffiliations(event.target.value)} className="mt-1" placeholder="Research lab, society" /></label><div className="flex gap-3 md:col-span-2"><Button type="submit" disabled={saving}>{saving ? "Saving…" : "Save profile"}</Button><Button type="button" variant="outline" onClick={onCancel}>Cancel</Button></div></form>;
}
