import { useState } from "react";
import {
  useInstitutions,
  useActivateInstitution,
  useDeactivateInstitution,
} from "@/hooks/useAuthQuery";
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
import { apiClient } from "@/api/client";
import {
  Building2,
  Power,
  PowerOff,
  RefreshCw,
  MapPin,
  Calendar,
  ExternalLink,
  Eye,
  Pencil,
  Plus,
  Trash2,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { Institution } from "@/types";

export default function Institutions() {
  const { data: institutions, isLoading, refetch } = useInstitutions();
  const activateMutation = useActivateInstitution();
  const deactivateMutation = useDeactivateInstitution();
  const [selectedInstitution, setSelectedInstitution] = useState<Institution | null>(null);
  const [dialogAction, setDialogAction] = useState<"activate" | "deactivate" | null>(null);
  const [crudMode, setCrudMode] = useState<"add" | "edit" | "details" | null>(null);

  function handleAction(institution: Institution, action: "activate" | "deactivate") {
    setSelectedInstitution(institution);
    setDialogAction(action);
  }

  function confirmAction() {
    if (!selectedInstitution || !dialogAction) return;

    if (dialogAction === "activate") {
      activateMutation.mutate(selectedInstitution.id, {
        onSuccess: () => {
          setSelectedInstitution(null);
          setDialogAction(null);
        },
      });
    } else {
      deactivateMutation.mutate(selectedInstitution.id, {
        onSuccess: () => {
          setSelectedInstitution(null);
          setDialogAction(null);
        },
      });
    }
  }

  async function saveInstitution(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const fields = new FormData(event.currentTarget);
    const values = { name: String(fields.get("name")), address: String(fields.get("address")) };
    if (crudMode === "add") await apiClient.createInstitution(values);
    if (crudMode === "edit" && selectedInstitution) await apiClient.updateInstitution(selectedInstitution.id, values);
    setCrudMode(null); setSelectedInstitution(null); void refetch();
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Building2 className="h-6 w-6" />
            Institutions
          </h1>
          <p className="text-slate-500 mt-1">
            Manage all institutions registered on the platform
          </p>
        </div>
        <div className="flex gap-2"><Button size="sm" onClick={() => { setSelectedInstitution(null); setCrudMode("add"); }} className="gap-1 bg-emerald-600 hover:bg-emerald-700"><Plus className="h-4 w-4" />Add Institution</Button><Button variant="outline" size="sm" onClick={() => refetch()} className="gap-1">
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button></div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Institutions</CardTitle>
          <CardDescription>
            {institutions?.length || 0} institutions found
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : !institutions?.length ? (
            <div className="text-center py-12">
              <Building2 className="h-12 w-12 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-1">
                No institutions yet
              </h3>
              <p className="text-slate-500">
                Institutions will appear here once they register.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Address</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {institutions.map((institution) => (
                    <TableRow key={institution.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          {institution.logo_url ? (
                            <img
                              src={institution.logo_url}
                              alt={institution.name}
                              className="h-10 w-10 rounded-lg object-cover border"
                            />
                          ) : (
                            <div className="h-10 w-10 rounded-lg bg-slate-100 flex items-center justify-center">
                              <Building2 className="h-5 w-5 text-slate-400" />
                            </div>
                          )}
                          <span className="font-medium">{institution.name}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-slate-500">
                          <MapPin className="h-3.5 w-3.5" />
                          <span className="text-sm">{institution.address}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={institution.is_active ? "default" : "secondary"}
                          className={
                            institution.is_active
                              ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-100"
                              : "bg-slate-100 text-slate-600 hover:bg-slate-100"
                          }
                        >
                          {institution.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-slate-500">
                          <Calendar className="h-3.5 w-3.5" />
                          <span className="text-sm">
                            {new Date(institution.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          {institution.logo_url && (
                            <Button variant="ghost" size="icon" className="h-8 w-8" asChild>
                              <a
                                href={institution.logo_url}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                <ExternalLink className="h-4 w-4" />
                              </a>
                            </Button>
                          )}
                          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => { setSelectedInstitution(institution); setCrudMode("details"); }}><Eye className="h-4 w-4" /></Button>
                          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => { setSelectedInstitution(institution); setCrudMode("edit"); }}><Pencil className="h-4 w-4" /></Button>
                          {institution.is_active ? (
                            <Button
                              variant="outline"
                              size="sm"
                              className="text-red-600 hover:text-red-700 hover:bg-red-50 gap-1"
                              onClick={() => handleAction(institution, "deactivate")}
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
                              onClick={() => handleAction(institution, "activate")}
                              disabled={activateMutation.isPending}
                            >
                              <Power className="h-3.5 w-3.5" />
                              Activate
                            </Button>
                          )}
                          <Button variant="ghost" size="icon" className="h-8 w-8 text-red-600" onClick={() => { if (window.confirm(`Delete ${institution.name}?`)) void apiClient.deleteInstitution(institution.id).then(() => refetch()); }}><Trash2 className="h-4 w-4" /></Button>
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

      {/* Confirmation Dialog */}
      <Dialog
        open={!!selectedInstitution && !!dialogAction}
        onOpenChange={() => {
          setSelectedInstitution(null);
          setDialogAction(null);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {dialogAction === "activate" ? "Activate Institution" : "Deactivate Institution"}
            </DialogTitle>
            <DialogDescription>
              {dialogAction === "activate"
                ? `Are you sure you want to activate "${selectedInstitution?.name}"? This will allow all its users to access the system.`
                : `Are you sure you want to deactivate "${selectedInstitution?.name}"? This will immediately lock out all users belonging to this institution.`}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setSelectedInstitution(null);
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
              {dialogAction === "activate" ? "Activate" : "Deactivate"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <Dialog open={!!crudMode} onOpenChange={(open) => !open && setCrudMode(null)}><DialogContent><DialogHeader><DialogTitle>{crudMode === "add" ? "Add Institution" : crudMode === "edit" ? "Edit Institution" : "Institution Details"}</DialogTitle></DialogHeader>{crudMode === "details" ? <div className="space-y-3 text-sm"><p><b>Name:</b> {selectedInstitution?.name}</p><p><b>Address:</b> {selectedInstitution?.address}</p><p><b>Status:</b> {selectedInstitution?.is_active ? "Active" : "Inactive"}</p></div> : <form onSubmit={saveInstitution} className="space-y-4"><Input name="name" required placeholder="Institution name" defaultValue={selectedInstitution?.name} /><Input name="address" required placeholder="Address" defaultValue={selectedInstitution?.address} /><DialogFooter><Button type="submit">Save</Button></DialogFooter></form>}</DialogContent></Dialog>
    </div>
  );
}
