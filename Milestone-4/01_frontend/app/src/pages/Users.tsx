import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  useInstitutionUsers,
  useCreateInstitutionUser,
  useActivateUser,
  useDeactivateUser,
  useDeleteInstitutionUser,
  useUpdateInstitutionUser,
} from "@/hooks/useAuthQuery";
import { apiClient } from "@/api/client";
import { createUserSchema, type CreateUserFormData } from "@/lib/schemas";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetFooter,
} from "@/components/ui/sheet";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Users as UsersIcon,
  Power,
  PowerOff,
  RefreshCw,
  UserPlus,
  Mail,
  Calendar,
  Filter,
  Eye,
  Pencil,
  Trash2,
} from "lucide-react";
import type { InstitutionUser } from "@/types";

type RoleFilter = "ALL" | "RESEARCHER" | "REVIEWER";

export default function Users() {
  const [roleFilter, setRoleFilter] = useState<RoleFilter>("ALL");
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<InstitutionUser | null>(null);
  const [dialogAction, setDialogAction] = useState<"activate" | "deactivate" | "delete" | null>(null);
  const [detailUser, setDetailUser] = useState<InstitutionUser | null>(null);
  const [editUser, setEditUser] = useState<InstitutionUser | null>(null);

  const { data: users, isLoading, refetch } = useInstitutionUsers(
    roleFilter === "ALL" ? undefined : roleFilter
  );
  const createMutation = useCreateInstitutionUser();
  const activateMutation = useActivateUser();
  const deactivateMutation = useDeactivateUser();
  const deleteMutation = useDeleteInstitutionUser();
  const updateMutation = useUpdateInstitutionUser();

  const form = useForm<CreateUserFormData>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      email: "",
      full_name: "",
      role: "RESEARCHER",
      description: "",
    },
  });

  function onSubmit(data: CreateUserFormData) {
    createMutation.mutate(
      {
        email: data.email,
        full_name: data.full_name,
        role: data.role,
        description: data.description || undefined,
      },
      {
        onSuccess: () => {
          setCreateDialogOpen(false);
          form.reset();
        },
      }
    );
  }

  function handleAction(user: InstitutionUser, action: "activate" | "deactivate" | "delete") {
    setSelectedUser(user);
    setDialogAction(action);
  }

  function confirmAction() {
    if (!selectedUser || !dialogAction) return;

    if (dialogAction === "activate") {
      activateMutation.mutate(selectedUser.id, {
        onSuccess: () => {
          setSelectedUser(null);
          setDialogAction(null);
        },
      });
    } else if (dialogAction === "deactivate") {
      deactivateMutation.mutate(selectedUser.id, {
        onSuccess: () => {
          setSelectedUser(null);
          setDialogAction(null);
        },
      });
    } else deleteMutation.mutate(selectedUser.id, { onSuccess: () => { setSelectedUser(null); setDialogAction(null); } });
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <UsersIcon className="h-6 w-6" />
            Users
          </h1>
          <p className="text-slate-500 mt-1">
            Manage researchers and reviewers under your institution
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => refetch()} className="gap-1">
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700 gap-1">
                <UserPlus className="h-4 w-4" />
                Add User
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Create New User</DialogTitle>
                <DialogDescription>
                  Add a researcher or reviewer. They will receive an email invite.
                </DialogDescription>
              </DialogHeader>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="full_name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Full Name</FormLabel>
                        <FormControl>
                          <Input placeholder="John Smith" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Email</FormLabel>
                        <FormControl>
                          <Input placeholder="user@university.edu" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="role"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Role</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select a role" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="RESEARCHER">Researcher</SelectItem>
                            <SelectItem value="REVIEWER">Reviewer</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Description (optional)</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Brief description or expertise"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <DialogFooter>
                    <Button type="submit" disabled={createMutation.isPending}>
                      {createMutation.isPending ? "Creating..." : "Create & Send Invite"}
                    </Button>
                  </DialogFooter>
                </form>
              </Form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2">
        <Filter className="h-4 w-4 text-slate-400" />
        <div className="flex items-center gap-1">
          {(["ALL", "RESEARCHER", "REVIEWER"] as RoleFilter[]).map((role) => (
            <Button
              key={role}
              variant={roleFilter === role ? "default" : "outline"}
              size="sm"
              onClick={() => setRoleFilter(role)}
              className={roleFilter === role ? "bg-emerald-600 hover:bg-emerald-700" : ""}
            >
              {role === "ALL" ? "All" : role.charAt(0) + role.slice(1).toLowerCase()}
            </Button>
          ))}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Institution Users</CardTitle>
          <CardDescription>
            {users?.length || 0} users found
            {roleFilter !== "ALL" && ` (${roleFilter.toLowerCase()}s)`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : !users?.length ? (
            <div className="text-center py-12">
              <UsersIcon className="h-12 w-12 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-1">
                No users found
              </h3>
              <p className="text-slate-500">
                {roleFilter !== "ALL"
                  ? `No ${roleFilter.toLowerCase()}s found.`
                  : "Add your first researcher or reviewer to get started."}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {users.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-full bg-emerald-100 flex items-center justify-center">
                            <span className="text-sm font-semibold text-emerald-700">
                              {user.full_name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <span className="font-medium">{user.full_name}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-slate-500">
                          <Mail className="h-3.5 w-3.5" />
                          <span className="text-sm">{user.email}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={
                            user.role === "RESEARCHER"
                              ? "border-blue-200 text-blue-700 bg-blue-50"
                              : "border-purple-200 text-purple-700 bg-purple-50"
                          }
                        >
                          {user.role}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Badge
                            variant={user.is_active ? "default" : "secondary"}
                            className={
                              user.is_active
                                ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-100"
                                : "bg-slate-100 text-slate-600 hover:bg-slate-100"
                            }
                          >
                            {user.is_active ? "Active" : "Inactive"}
                          </Badge>
                          {!user.is_verified && (
                            <Badge variant="outline" className="border-amber-200 text-amber-700 bg-amber-50">
                              Pending
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-slate-500">
                          <Calendar className="h-3.5 w-3.5" />
                          <span className="text-sm">
                            {new Date(user.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                        {user.role === "RESEARCHER" && <Button variant="ghost" size="icon" onClick={() => setDetailUser(user)}><Eye className="h-4 w-4" /></Button>}
                        <Button variant="ghost" size="icon" onClick={() => setEditUser(user)}><Pencil className="h-4 w-4" /></Button>
                        {user.is_active ? (
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50 gap-1"
                            onClick={() => handleAction(user, "deactivate")}
                            disabled={deactivateMutation.isPending}
                          >
                            <PowerOff className="h-3.5 w-3.5" />
                            Deactivate
                          </Button>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50 gap-1"
                            onClick={() => handleAction(user, "activate")}
                            disabled={activateMutation.isPending}
                          >
                            <Power className="h-3.5 w-3.5" />
                            Activate
                          </Button>
                        )}
                        <Button variant="ghost" size="icon" className="text-red-600 hover:text-red-700" onClick={() => handleAction(user, "delete")}><Trash2 className="h-4 w-4" /></Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Confirmation Sheet */}
      <Sheet
        open={!!selectedUser && !!dialogAction}
        onOpenChange={() => {
          setSelectedUser(null);
          setDialogAction(null);
        }}
      >
        <SheetContent>
          <SheetHeader>
            <SheetTitle>
              {dialogAction === "activate" ? "Activate User" : dialogAction === "delete" ? "Delete User" : "Deactivate User"}
            </SheetTitle>
            <SheetDescription>
              {dialogAction === "activate"
                ? `Activate "${selectedUser?.full_name}"? They will regain access to the system.`
                : dialogAction === "delete" ? `Delete "${selectedUser?.full_name}" permanently? This cannot be undone.` : `Deactivate "${selectedUser?.full_name}"? They will lose access immediately.`}
            </SheetDescription>
          </SheetHeader>
          <div className="py-6">
            <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4 space-y-2">
              <p className="text-sm">
                <span className="font-medium">Name:</span> {selectedUser?.full_name}
              </p>
              <p className="text-sm">
                <span className="font-medium">Email:</span> {selectedUser?.email}
              </p>
              <p className="text-sm">
                <span className="font-medium">Role:</span> {selectedUser?.role}
              </p>
            </div>
          </div>
          <SheetFooter>
            <Button
              variant="outline"
              onClick={() => {
                setSelectedUser(null);
                setDialogAction(null);
              }}
            >
              Cancel
            </Button>
            <Button
              variant={dialogAction === "activate" ? "default" : "destructive"}
              onClick={confirmAction}
              disabled={activateMutation.isPending || deactivateMutation.isPending}
              className={dialogAction === "activate" ? "bg-emerald-600 hover:bg-emerald-700" : ""}
            >
              {dialogAction === "activate" ? "Activate" : dialogAction === "delete" ? "Delete" : "Deactivate"}
            </Button>
          </SheetFooter>
        </SheetContent>
      </Sheet>
      <Dialog open={!!editUser} onOpenChange={(open) => !open && setEditUser(null)}>
        <DialogContent><DialogHeader><DialogTitle>Edit User</DialogTitle><DialogDescription>Update the researcher's basic account details.</DialogDescription></DialogHeader>
          <form onSubmit={(event) => { event.preventDefault(); const values = new FormData(event.currentTarget); if (editUser) updateMutation.mutate({ userId: editUser.id, data: { full_name: String(values.get("full_name")), description: String(values.get("description") || "") || null } }, { onSuccess: () => setEditUser(null) }); }} className="space-y-4"><Input name="full_name" defaultValue={editUser?.full_name} required /><Textarea name="description" defaultValue={editUser?.description || ""} placeholder="Description" /><DialogFooter><Button type="submit" disabled={updateMutation.isPending}>{updateMutation.isPending ? "Saving..." : "Save changes"}</Button></DialogFooter></form>
        </DialogContent>
      </Dialog>
      <ResearcherDetailsDialog user={detailUser} onClose={() => setDetailUser(null)} />
    </div>
  );
}

function ResearcherDetailsDialog({ user, onClose }: { user: InstitutionUser | null; onClose: () => void }) {
  const queryClient = useQueryClient();
  const profile = useQuery({ queryKey: ["researcher-profile", user?.id], queryFn: () => apiClient.getInstitutionResearcherProfile(user!.id), enabled: !!user });
  const update = useMutation({ mutationFn: (data: { department: string | null; skills: string[]; research_interests: string[]; affiliations: string[] }) => apiClient.updateInstitutionResearcherProfile(user!.id, data), onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["researcher-profile", user?.id] }) });
  const list = (value: FormDataEntryValue | null) => String(value || "").split(",").map((item) => item.trim()).filter(Boolean);
  return <Dialog open={!!user} onOpenChange={(open) => !open && onClose()}><DialogContent className="max-w-lg"><DialogHeader><DialogTitle>Researcher Details</DialogTitle><DialogDescription>{user?.full_name} · {user?.email}</DialogDescription></DialogHeader>{profile.isLoading ? <p className="text-sm text-slate-500">Loading academic profile...</p> : <form onSubmit={(event) => { event.preventDefault(); const values = new FormData(event.currentTarget); update.mutate({ department: String(values.get("department") || "") || null, skills: list(values.get("skills")), research_interests: list(values.get("interests")), affiliations: list(values.get("affiliations")) }); }} className="grid gap-4"><label className="text-sm font-medium">Department<Input name="department" defaultValue={profile.data?.department || ""} className="mt-1" /></label><label className="text-sm font-medium">Skills<Input name="skills" defaultValue={profile.data?.skills.join(", ") || ""} className="mt-1" /></label><label className="text-sm font-medium">Research Interests<Input name="interests" defaultValue={profile.data?.research_interests.join(", ") || ""} className="mt-1" /></label><label className="text-sm font-medium">Affiliations<Input name="affiliations" defaultValue={profile.data?.affiliations.join(", ") || ""} className="mt-1" /></label><DialogFooter><Button type="submit" disabled={update.isPending}>{update.isPending ? "Saving..." : "Save academic profile"}</Button></DialogFooter></form>}</DialogContent></Dialog>;
}
