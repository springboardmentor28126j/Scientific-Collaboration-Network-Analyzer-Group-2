import { useState } from "react";
import { useParams, useNavigate } from "react-router";
import { useAuthStore } from "@/stores/authStore";
import {
  usePublication,
  useUpdatePublication,
  useDeletePublication,
  useSubmitPublication,
  usePublicationAuthors,
  useAddPublicationAuthor,
  useRemovePublicationAuthor,
  usePublicationHistory,
  useResearchers,
} from "@/hooks/usePublicationQuery";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { publicationTypes } from "@/lib/schemas";
import {
  ArrowLeft,
  FileText,
  Download,
  Trash2,
  Edit,
  Send,
  UserPlus,
  Users,
  History,
  UserMinus,
  Check,
} from "lucide-react";
import { format } from "date-fns";

const statusColors: Record<string, string> = {
  DRAFT: "bg-slate-100 text-slate-800",
  SUBMITTED: "bg-blue-100 text-blue-800",
  UNDER_REVIEW: "bg-amber-100 text-amber-800",
  REVISION_REQUIRED: "bg-orange-100 text-orange-800",
  ACCEPTED: "bg-emerald-100 text-emerald-800",
  REJECTED: "bg-red-100 text-red-800",
  PUBLISHED: "bg-purple-100 text-purple-800",
  ARCHIVED: "bg-gray-100 text-gray-800",
};

export default function PublicationDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);

  const { data: publication, isLoading } = usePublication(id!);
  const { data: authors } = usePublicationAuthors(id!);
  const { data: history } = usePublicationHistory(id!);

  const { mutateAsync: updatePublication } = useUpdatePublication();
  const { mutateAsync: deletePublication } = useDeletePublication();
  const { mutateAsync: submitPublication } = useSubmitPublication();
  const { mutateAsync: addAuthor } = useAddPublicationAuthor();
  const { mutateAsync: removeAuthor } = useRemovePublicationAuthor();

  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editData, setEditData] = useState({
    title: "",
    abstract: "",
    publication_type: "",
    doi: "",
  });

  const [isAuthorDialogOpen, setIsAuthorDialogOpen] = useState(false);
  const [authorSearch, setAuthorSearch] = useState("");
  const { data: researchers } = useResearchers(authorSearch);

  if (isLoading) {
    return <div className="p-8 text-center text-slate-500">Loading publication...</div>;
  }

  if (!publication) {
    return <div className="p-8 text-center text-red-500">Publication not found</div>;
  }

  const isDraft = publication.status === "DRAFT";
  const isCreator = publication.created_by === user?.id;

  const handleEditOpen = () => {
    setEditData({
      title: publication.title,
      abstract: publication.abstract,
      publication_type: publication.publication_type,
      doi: publication.doi || "",
    });
    setIsEditDialogOpen(true);
  };

  const handleEditSave = async () => {
    await updatePublication({
      id: publication.id,
      data: {
        title: editData.title,
        abstract: editData.abstract,
        publication_type: editData.publication_type as any,
        doi: editData.doi || null,
      },
    });
    setIsEditDialogOpen(false);
  };

  const handleDelete = async () => {
    if (confirm("Are you sure you want to delete this draft?")) {
      await deletePublication(publication.id);
      navigate("/dashboard/research");
    }
  };

  const handleSubmit = async () => {
    if (confirm("Are you sure you want to submit this publication for review?")) {
      await submitPublication(publication.id);
    }
  };

  const handleAddAuthor = async (researcher_id: string) => {
    const nextOrder = (authors?.length || 0) + 1;
    await addAuthor({
      id: publication.id,
      data: {
        researcher_id,
        author_order: nextOrder,
        is_corresponding_author: nextOrder === 1,
      },
    });
  };

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/dashboard/research")}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
              {publication.title}
            </h1>
            <Badge className={statusColors[publication.status] || "bg-slate-100"}>
              {publication.status.replace("_", " ")}
            </Badge>
          </div>
          <p className="text-slate-500 mt-1 flex items-center gap-2">
            <span>{publication.publication_type.replace("_", " ")}</span>
            {publication.doi && (
              <>
                <span>•</span>
                <span>DOI: {publication.doi}</span>
              </>
            )}
            <span>•</span>
            <span>Created {format(new Date(publication.created_at), "MMM d, yyyy")}</span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          {publication.pdf_url && (
            <Button variant="outline" asChild>
              <a href={`${API_BASE_URL}${publication.pdf_url}`} target="_blank" rel="noopener noreferrer">
                <Download className="w-4 h-4 mr-2" />
                Download PDF
              </a>
            </Button>
          )}

          {isDraft && isCreator && (
            <>
              <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" onClick={handleEditOpen}>
                    <Edit className="w-4 h-4 mr-2" />
                    Edit
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Edit Draft Publication</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label>Title</Label>
                      <Input
                        value={editData.title}
                        onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Abstract</Label>
                      <Textarea
                        className="h-32"
                        value={editData.abstract}
                        onChange={(e) => setEditData({ ...editData, abstract: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Type</Label>
                      <Select
                        value={editData.publication_type}
                        onValueChange={(val) => setEditData({ ...editData, publication_type: val })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {publicationTypes.map((t) => (
                            <SelectItem key={t} value={t}>
                              {t.replace("_", " ")}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>DOI (Optional)</Label>
                      <Input
                        value={editData.doi}
                        onChange={(e) => setEditData({ ...editData, doi: e.target.value })}
                      />
                    </div>
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button variant="ghost" onClick={() => setIsEditDialogOpen(false)}>Cancel</Button>
                    <Button onClick={handleEditSave}>Save Changes</Button>
                  </div>
                </DialogContent>
              </Dialog>

              <Button variant="destructive" onClick={handleDelete}>
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </Button>

              <Button onClick={handleSubmit} className="bg-emerald-600 hover:bg-emerald-700">
                <Send className="w-4 h-4 mr-2" />
                Submit for Review
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-slate-500" />
                Abstract
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-wrap text-slate-700 dark:text-slate-300">
                {publication.abstract}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5 text-slate-500" />
                Co-Authors
              </CardTitle>
              {isDraft && isCreator && (
                <Dialog open={isAuthorDialogOpen} onOpenChange={setIsAuthorDialogOpen}>
                  <DialogTrigger asChild>
                    <Button variant="outline" size="sm">
                      <UserPlus className="w-4 h-4 mr-2" />
                      Add Author
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Add Co-Author</DialogTitle>
                      <DialogDescription>Search for researchers to add as co-authors.</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <Input
                        placeholder="Search by name or email..."
                        value={authorSearch}
                        onChange={(e) => setAuthorSearch(e.target.value)}
                      />
                      <div className="space-y-2 max-h-60 overflow-y-auto">
                        {researchers?.map((researcher) => {
                          const isAlreadyAdded = authors?.some((a) => a.researcher_id === researcher.id);
                          return (
                            <div key={researcher.id} className="flex items-center justify-between p-2 border rounded">
                              <div>
                                <p className="font-medium">{researcher.full_name}</p>
                                <p className="text-xs text-slate-500">{researcher.institution_name || "Unknown Institution"}</p>
                              </div>
                              <Button
                                size="sm"
                                variant={isAlreadyAdded ? "secondary" : "default"}
                                disabled={isAlreadyAdded}
                                onClick={() => handleAddAuthor(researcher.id)}
                              >
                                {isAlreadyAdded ? <Check className="w-4 h-4" /> : "Add"}
                              </Button>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              )}
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {authors?.length === 0 ? (
                  <p className="text-slate-500 italic">No authors added yet.</p>
                ) : (
                  authors?.sort((a, b) => a.author_order - b.author_order).map((author) => (
                    <div key={author.researcher_id} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold">
                          {author.author_order}
                        </div>
                        <div>
                          <p className="font-medium">
                            {author.full_name}
                            {author.is_corresponding_author && (
                              <Badge variant="outline" className="ml-2 text-xs">Corresponding</Badge>
                            )}
                          </p>
                          <p className="text-xs text-slate-500">{author.institution}</p>
                        </div>
                      </div>
                      {isDraft && isCreator && author.researcher_id !== user?.id && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-red-500 hover:text-red-700 hover:bg-red-50"
                          onClick={() => removeAuthor({ id: publication.id, researcher_id: author.researcher_id })}
                        >
                          <UserMinus className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="w-5 h-5 text-slate-500" />
                History
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {history?.length === 0 ? (
                  <p className="text-slate-500 italic text-sm">No history available.</p>
                ) : (
                  history?.map((entry) => (
                    <div key={entry.id} className="relative pl-6 border-l-2 border-slate-200 dark:border-slate-700 pb-4 last:pb-0">
                      <div className="absolute w-3 h-3 bg-slate-200 dark:bg-slate-700 rounded-full -left-[7px] top-1.5" />
                      <p className="text-sm font-medium text-slate-900 dark:text-white">
                        {entry.action.replace(/_/g, " ")}
                      </p>
                      <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                        {entry.description}
                      </p>
                      <div className="flex items-center gap-2 mt-2 text-xs text-slate-500">
                        {entry.user && <span className="font-medium">{entry.user.full_name}</span>}
                        {entry.user && <span>•</span>}
                        <span>{format(new Date(entry.created_at), "MMM d, h:mm a")}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
