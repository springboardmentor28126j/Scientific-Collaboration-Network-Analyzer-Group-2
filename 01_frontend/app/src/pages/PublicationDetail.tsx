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
  usePublishPublication,
  useConference,
  useCreateConference,
  useUpdateConference,
  useSubmitEditorialDecision,
  useArchivePublication,
  useResearchers,
  useDownloadPdf,
} from "@/hooks/usePublicationQuery";
import {
  useReviewers,
  useReviewAssignments,
  useAssignReviewers,
  useSubmitReview,
  usePublicationReviews,
} from "@/hooks/useReviewQuery";
import type { ConferenceCreate, EditorialDecisionCreate } from "@/types";
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
import { PublicationReferences } from "@/components/PublicationReferences";
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
  ClipboardCheck,
  MessageSquareQuote,
  Star,
  Globe2,
  Archive,
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
  const { mutateAsync: assignReviewers } = useAssignReviewers();

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

  const [isReviewerDialogOpen, setIsReviewerDialogOpen] = useState(false);
  const [reviewerSearch, setReviewerSearch] = useState("");
  const { data: reviewers } = useReviewers(reviewerSearch);
  const { data: reviewAssignments } = useReviewAssignments(id!);
  const { data: reviews } = usePublicationReviews(id!);

  const { mutateAsync: submitReview } = useSubmitReview();

  const [isReviewFormOpen, setIsReviewFormOpen] = useState(false);
  const [reviewData, setReviewData] = useState({
    decision: "ACCEPT",
    score: 3,
    strengths: "",
    weaknesses: "",
    comments: "",
    recommendation: "",
  });

  const { data: conference } = useConference(id!);
  const { mutateAsync: publishPublication } = usePublishPublication();
  const { mutateAsync: createConference } = useCreateConference();
  const { mutateAsync: updateConference } = useUpdateConference();
  const { mutateAsync: submitEditorialDecision } = useSubmitEditorialDecision();
  const { mutateAsync: archivePublication } = useArchivePublication();
  const { mutateAsync: downloadPdf, isPending: isDownloading } = useDownloadPdf();

  const [isDecisionDialogOpen, setIsDecisionDialogOpen] = useState(false);
  const [decisionData, setDecisionData] = useState<EditorialDecisionCreate>({
    decision: "ACCEPTED",
    editor_note: "",
  });

  const [isConferenceDialogOpen, setIsConferenceDialogOpen] = useState(false);
  const [conferenceData, setConferenceData] = useState<ConferenceCreate>({
    conference_name: "",
    venue: "",
    city: "",
    country: "",
    conference_date: "",
    publication_date: "",
    publisher: "",
    proceedings_name: "",
    isbn: "",
    issn: "",
    outcome: "PRESENTED",
    remarks: "",
  });

  if (isLoading) {
    return <div className="p-8 text-center text-slate-500">Loading publication...</div>;
  }

  if (!publication) {
    return <div className="p-8 text-center text-red-500">Publication not found</div>;
  }

  const isDraft = publication.status === "DRAFT";
  const isCreator = publication.created_by === user?.id;
  const isSuperAdmin = user?.role === "SUPER_ADMIN";
  const isAssignableStatus = ["SUBMITTED", "UNDER_REVIEW", "REVISION_REQUIRED"].includes(publication.status);

  const myAssignment = reviewAssignments?.find(r => r.reviewer_id === user?.id);
  const canReview = myAssignment && (myAssignment.status === "PENDING" || myAssignment.status === "IN_PROGRESS");

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
      navigate("/dashboard/publications");
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

  const handleAssignReviewer = async (reviewer_id: string) => {
    await assignReviewers({
      publicationId: publication.id,
      reviewerIds: [reviewer_id],
    });
  };

  const handleReviewSubmit = async () => {
    if (!myAssignment) return;
    await submitReview({
      assignment_id: myAssignment.id,
      decision: reviewData.decision,
      score: reviewData.score,
      strengths: reviewData.strengths,
      weaknesses: reviewData.weaknesses,
      comments: reviewData.comments,
      recommendation: reviewData.recommendation,
    });
    setIsReviewFormOpen(false);
  };

  const handlePublish = async () => {
    await publishPublication(id!);
  };

  const handleArchive = async () => {
    await archivePublication(id!);
  };

  const handleConferenceOpen = () => {
    if (conference) {
      setConferenceData({
        conference_name: conference.conference_name,
        venue: conference.venue,
        city: conference.city,
        country: conference.country,
        conference_date: conference.conference_date,
        publication_date: conference.publication_date,
        publisher: conference.publisher,
        proceedings_name: conference.proceedings_name,
        isbn: conference.isbn,
        issn: conference.issn,
        outcome: conference.outcome,
        remarks: conference.remarks,
      });
    } else {
      setConferenceData({
        conference_name: "",
        venue: "",
        city: "",
        country: "",
        conference_date: "",
        publication_date: publication?.published_at ? format(new Date(publication.published_at), "yyyy-MM-dd") : "",
        publisher: "",
        proceedings_name: "",
        isbn: "",
        issn: "",
        outcome: "PRESENTED",
        remarks: "",
      });
    }
    setIsConferenceDialogOpen(true);
  };

  const handleConferenceSubmit = async () => {
    if (conference) {
      await updateConference({ id: id!, data: conferenceData });
    } else {
      await createConference({ id: id!, data: conferenceData });
    }
    setIsConferenceDialogOpen(false);
  };

  const handleDecisionSubmit = async () => {
    await submitEditorialDecision({ id: id!, data: decisionData });
    setIsDecisionDialogOpen(false);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/dashboard/publications")}>
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
            <Button variant="outline" onClick={() => downloadPdf(publication.id)} disabled={isDownloading}>
              <Download className="w-4 h-4 mr-2" />
              {isDownloading ? "Downloading..." : "Download PDF"}
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

          {isSuperAdmin && (publication.status === "UNDER_REVIEW" || publication.status === "SUBMITTED" || publication.status === "REVISION_REQUIRED") && (
            <Dialog open={isDecisionDialogOpen} onOpenChange={setIsDecisionDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  <ClipboardCheck className="w-4 h-4 mr-2" />
                  Editorial Decision
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Make Editorial Decision</DialogTitle>
                  <DialogDescription>
                    Accept, reject, or request revisions for this publication.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label>Decision</Label>
                    <Select value={decisionData.decision} onValueChange={(val) => setDecisionData({ ...decisionData, decision: val })}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ACCEPTED">Accept</SelectItem>
                        <SelectItem value="REVISION_REQUIRED">Request Revision</SelectItem>
                        <SelectItem value="REJECTED">Reject</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Editor's Note (Optional)</Label>
                    <Textarea 
                      placeholder="Feedback or reason for this decision..." 
                      value={decisionData.editor_note} 
                      onChange={(e) => setDecisionData({ ...decisionData, editor_note: e.target.value })}
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-2 mt-4">
                  <Button variant="ghost" onClick={() => setIsDecisionDialogOpen(false)}>Cancel</Button>
                  <Button onClick={handleDecisionSubmit}>Submit Decision</Button>
                </div>
              </DialogContent>
            </Dialog>
          )}

          {isSuperAdmin && publication.status === "ACCEPTED" && (
            <Button onClick={handlePublish} className="bg-purple-600 hover:bg-purple-700">
              <Globe2 className="w-4 h-4 mr-2" />
              Publish
            </Button>
          )}

          {isSuperAdmin && publication.status === "PUBLISHED" && (
            <Button onClick={handleArchive} variant="outline" className="border-gray-300 text-gray-700 hover:bg-gray-100">
              <Archive className="w-4 h-4 mr-2" />
              Archive
            </Button>
          )}

          {canReview && (
            <Dialog open={isReviewFormOpen} onOpenChange={setIsReviewFormOpen}>
              <DialogTrigger asChild>
                <Button className="bg-amber-600 hover:bg-amber-700 text-white">
                  <Star className="w-4 h-4 mr-2" />
                  Submit Review
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Submit Review</DialogTitle>
                  <DialogDescription>Provide your feedback and recommendation for this publication.</DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Decision</Label>
                      <Select value={reviewData.decision} onValueChange={(val) => setReviewData({ ...reviewData, decision: val })}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="ACCEPT">Accept</SelectItem>
                          <SelectItem value="MINOR_REVISION">Minor Revision</SelectItem>
                          <SelectItem value="MAJOR_REVISION">Major Revision</SelectItem>
                          <SelectItem value="REJECT">Reject</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Score (1-5)</Label>
                      <Input
                        type="number"
                        min="1" max="5"
                        value={reviewData.score}
                        onChange={(e) => setReviewData({ ...reviewData, score: Number(e.target.value) })}
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Strengths</Label>
                    <Textarea
                      className="h-20"
                      value={reviewData.strengths}
                      onChange={(e) => setReviewData({ ...reviewData, strengths: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Weaknesses</Label>
                    <Textarea
                      className="h-20"
                      value={reviewData.weaknesses}
                      onChange={(e) => setReviewData({ ...reviewData, weaknesses: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Comments for Authors</Label>
                    <Textarea
                      className="h-32"
                      value={reviewData.comments}
                      onChange={(e) => setReviewData({ ...reviewData, comments: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Confidential Recommendation to Editor</Label>
                    <Textarea
                      className="h-20"
                      value={reviewData.recommendation}
                      onChange={(e) => setReviewData({ ...reviewData, recommendation: e.target.value })}
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-2 mt-4">
                  <Button variant="ghost" onClick={() => setIsReviewFormOpen(false)}>Cancel</Button>
                  <Button onClick={handleReviewSubmit}>Submit Review</Button>
                </div>
              </DialogContent>
            </Dialog>
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

          <PublicationReferences publicationId={publication.id} readOnly={!(isDraft && isCreator)} />

          {isSuperAdmin && (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <ClipboardCheck className="w-5 h-5 text-slate-500" />
                  Assigned Reviewers
                </CardTitle>
                {isAssignableStatus && (
                  <Dialog open={isReviewerDialogOpen} onOpenChange={setIsReviewerDialogOpen}>
                    <DialogTrigger asChild>
                      <Button variant="outline" size="sm">
                        <UserPlus className="w-4 h-4 mr-2" />
                        Assign Reviewer
                      </Button>
                    </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Assign Reviewer</DialogTitle>
                      <DialogDescription>Search for verified reviewers to assign to this publication.</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <Input
                        placeholder="Search by name or email..."
                        value={reviewerSearch}
                        onChange={(e) => setReviewerSearch(e.target.value)}
                      />
                      <div className="space-y-2 max-h-60 overflow-y-auto">
                        {reviewers?.map((reviewer) => {
                          const isAlreadyAssigned = reviewAssignments?.some((r) => r.reviewer_id === reviewer.id);
                          return (
                            <div key={reviewer.id} className="flex items-center justify-between p-2 border rounded">
                              <div>
                                <p className="font-medium">{reviewer.full_name}</p>
                                <p className="text-xs text-slate-500">{reviewer.institution_name || "Unknown Institution"}</p>
                              </div>
                              <Button
                                size="sm"
                                variant={isAlreadyAssigned ? "secondary" : "default"}
                                disabled={isAlreadyAssigned}
                                onClick={() => handleAssignReviewer(reviewer.id)}
                              >
                                {isAlreadyAssigned ? <Check className="w-4 h-4" /> : "Assign"}
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
                  {reviewAssignments?.length === 0 ? (
                    <p className="text-slate-500 italic">No reviewers assigned yet.</p>
                  ) : (
                    reviewAssignments?.map((assignment) => (
                      <div key={assignment.id} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-sm font-bold uppercase">
                            {assignment.reviewer_name.charAt(0)}
                          </div>
                          <div>
                            <p className="font-medium">{assignment.reviewer_name}</p>
                            <p className="text-xs text-slate-500">{assignment.reviewer_email}</p>
                          </div>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {assignment.status}
                        </Badge>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {reviews && reviews.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquareQuote className="w-5 h-5 text-slate-500" />
                  Submitted Reviews
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {reviews.map((rev) => (
                    <div key={rev.id} className="p-4 border rounded-lg bg-slate-50 dark:bg-slate-800">
                      <div className="flex items-center justify-between mb-3 border-b pb-3">
                        <div className="flex items-center gap-3">
                          <Badge variant="outline" className="text-sm font-semibold">
                            {rev.decision.replace(/_/g, " ")}
                          </Badge>
                          <div className="flex items-center text-amber-500 text-sm font-bold">
                            <Star className="w-4 h-4 fill-current mr-1" />
                            {rev.score}/5
                          </div>
                        </div>
                        <span className="text-xs text-slate-500">
                          {format(new Date(rev.submitted_at), "MMM d, yyyy")}
                        </span>
                      </div>
                      
                      <div className="space-y-3 text-sm">
                        {rev.strengths && (
                          <div>
                            <span className="font-semibold text-slate-700 dark:text-slate-300">Strengths: </span>
                            <span className="text-slate-600 dark:text-slate-400">{rev.strengths}</span>
                          </div>
                        )}
                        {rev.weaknesses && (
                          <div>
                            <span className="font-semibold text-slate-700 dark:text-slate-300">Weaknesses: </span>
                            <span className="text-slate-600 dark:text-slate-400">{rev.weaknesses}</span>
                          </div>
                        )}
                        {rev.comments && (
                          <div className="pt-2 border-t border-slate-200 dark:border-slate-700 border-dashed">
                            <span className="font-semibold block mb-1 text-slate-700 dark:text-slate-300">Comments:</span>
                            <p className="text-slate-600 dark:text-slate-400 whitespace-pre-wrap">{rev.comments}</p>
                          </div>
                        )}
                        {rev.recommendation && (isSuperAdmin || (myAssignment?.id === rev.assignment_id)) && (
                          <div className="pt-2 mt-2 border-t border-amber-200 bg-amber-50 p-2 rounded text-amber-900">
                            <span className="font-semibold block mb-1">Confidential Recommendation:</span>
                            <p className="whitespace-pre-wrap">{rev.recommendation}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {(isSuperAdmin || conference) && publication.status === "PUBLISHED" && (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Globe2 className="w-5 h-5 text-slate-500" />
                  Conference Details
                </CardTitle>
                {isSuperAdmin && (
                  <Dialog open={isConferenceDialogOpen} onOpenChange={setIsConferenceDialogOpen}>
                  <DialogTrigger asChild>
                    <Button variant="outline" size="sm" onClick={handleConferenceOpen}>
                      {conference ? "Edit Details" : "Add Details"}
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                      <DialogTitle>{conference ? "Edit Conference Details" : "Add Conference Details"}</DialogTitle>
                      <DialogDescription>Details about where this publication was presented or published.</DialogDescription>
                    </DialogHeader>
                    <div className="grid grid-cols-2 gap-4 py-4">
                      <div className="space-y-2">
                        <Label>Conference/Journal Name</Label>
                        <Input value={conferenceData.conference_name} onChange={e => setConferenceData({...conferenceData, conference_name: e.target.value})} />
                      </div>
                      <div className="space-y-2">
                        <Label>Venue</Label>
                        <Input value={conferenceData.venue} onChange={e => setConferenceData({...conferenceData, venue: e.target.value})} />
                      </div>
                      <div className="space-y-2">
                        <Label>City</Label>
                        <Input value={conferenceData.city} onChange={e => setConferenceData({...conferenceData, city: e.target.value})} />
                      </div>
                      <div className="space-y-2">
                        <Label>Country</Label>
                        <Input value={conferenceData.country} onChange={e => setConferenceData({...conferenceData, country: e.target.value})} />
                      </div>
                      <div className="space-y-2">
                        <Label>Conference Date</Label>
                        <Input type="date" value={conferenceData.conference_date} onChange={e => setConferenceData({...conferenceData, conference_date: e.target.value})} />
                      </div>
                      <div className="space-y-2">
                        <Label>Publication Date</Label>
                        <Input type="date" value={conferenceData.publication_date} onChange={e => setConferenceData({...conferenceData, publication_date: e.target.value})} />
                      </div>
                      <div className="space-y-2">
                        <Label>Publisher</Label>
                        <Input value={conferenceData.publisher} onChange={e => setConferenceData({...conferenceData, publisher: e.target.value})} />
                      </div>
                      <div className="space-y-2">
                        <Label>Proceedings Name</Label>
                        <Input value={conferenceData.proceedings_name} onChange={e => setConferenceData({...conferenceData, proceedings_name: e.target.value})} />
                      </div>
                      <div className="space-y-2">
                        <Label>ISBN</Label>
                        <Input value={conferenceData.isbn} onChange={e => setConferenceData({...conferenceData, isbn: e.target.value})} />
                      </div>
                      <div className="space-y-2">
                        <Label>ISSN</Label>
                        <Input value={conferenceData.issn} onChange={e => setConferenceData({...conferenceData, issn: e.target.value})} />
                      </div>
                      <div className="space-y-2 col-span-2">
                        <Label>Outcome</Label>
                        <Select value={conferenceData.outcome} onValueChange={(val) => setConferenceData({ ...conferenceData, outcome: val })}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="PRESENTED">Presented</SelectItem>
                            <SelectItem value="PUBLISHED_IN_PROCEEDINGS">Published in Proceedings</SelectItem>
                            <SelectItem value="BEST_PAPER">Best Paper</SelectItem>
                            <SelectItem value="HONORABLE_MENTION">Honorable Mention</SelectItem>
                            <SelectItem value="CANCELLED">Cancelled</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2 col-span-2">
                        <Label>Remarks</Label>
                        <Textarea value={conferenceData.remarks} onChange={e => setConferenceData({...conferenceData, remarks: e.target.value})} />
                      </div>
                    </div>
                    <div className="flex justify-end gap-2 mt-4">
                      <Button variant="ghost" onClick={() => setIsConferenceDialogOpen(false)}>Cancel</Button>
                      <Button onClick={handleConferenceSubmit}>Save Conference Details</Button>
                    </div>
                  </DialogContent>
                </Dialog>
                )}
              </CardHeader>
              <CardContent>
                {!conference ? (
                  <p className="text-sm text-slate-500 italic">No conference details added yet.</p>
                ) : (
                  <div className="grid grid-cols-2 gap-y-3 text-sm">
                    <div><span className="font-semibold text-slate-600">Name:</span> {conference.conference_name}</div>
                    <div><span className="font-semibold text-slate-600">Venue:</span> {conference.venue}, {conference.city}, {conference.country}</div>
                    <div><span className="font-semibold text-slate-600">Conference Date:</span> {conference.conference_date}</div>
                    <div><span className="font-semibold text-slate-600">Publication Date:</span> {conference.publication_date}</div>
                    {conference.publisher && <div><span className="font-semibold text-slate-600">Publisher:</span> {conference.publisher}</div>}
                    {conference.proceedings_name && <div><span className="font-semibold text-slate-600">Proceedings:</span> {conference.proceedings_name}</div>}
                    {conference.isbn && <div><span className="font-semibold text-slate-600">ISBN:</span> {conference.isbn}</div>}
                    {conference.issn && <div><span className="font-semibold text-slate-600">ISSN:</span> {conference.issn}</div>}
                    <div>
                      <span className="font-semibold text-slate-600">Outcome:</span>
                      <Badge variant="secondary" className="ml-2">{conference.outcome}</Badge>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
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
