import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { 
  useReferences, 
  useAddReference, 
  useDeleteReference, 
  useSearchCatalog,
} from "@/hooks/usePublicationQuery";
import { getCatalogPublication } from "@/api/publication";
import { referenceSchema, type ReferenceFormData } from "@/lib/schemas";
import { useAuthStore } from "@/stores/authStore";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { BookOpen, Search, User, Trash2, Plus, Quote, Loader2, Calendar, Tag, Link as LinkIcon } from "lucide-react";
import { useDebounce } from "@/hooks/useDebounce";

interface PublicationReferencesProps {
  publicationId: string;
  readOnly?: boolean;
}

export function PublicationReferences({ publicationId, readOnly = false }: PublicationReferencesProps) {
  const user = useAuthStore((state) => state.user);
  const { data: references, isLoading } = useReferences(publicationId);
  const { mutateAsync: addReference, isPending: isAdding } = useAddReference(publicationId);
  const { mutateAsync: deleteReference, isPending: isDeleting } = useDeleteReference(publicationId);

  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearch = useDebounce(searchQuery, 300);
  
  const { data: searchResults, isFetching: isSearching } = useSearchCatalog(debouncedSearch);
  const [isFetchingDetails, setIsFetchingDetails] = useState(false);

  const form = useForm<ReferenceFormData>({
    resolver: zodResolver(referenceSchema),
    defaultValues: {
      title: "",
      authors: "",
      publication_name: "",
      year: new Date().getFullYear(),
      doi: "",
      url: "",
    },
  });

  // Reset form when dialog opens/closes
  useEffect(() => {
    if (!isOpen) {
      form.reset();
      setSearchQuery("");
    }
  }, [isOpen, form]);

  const handleSelectSearchResult = async (catalogId: string) => {
    try {
      setIsFetchingDetails(true);
      const details = await getCatalogPublication(catalogId);
      form.setValue("title", details.title, { shouldValidate: true });
      form.setValue("authors", details.authors, { shouldValidate: true });
      form.setValue("year", details.year, { shouldValidate: true });
      form.setValue("publication_name", details.publication_name || "", { shouldValidate: true });
      form.setValue("doi", details.doi || "", { shouldValidate: true });
      form.setValue("url", details.url || "", { shouldValidate: true });
      setSearchQuery(""); // Clear search so results hide
    } catch (error) {
      console.error("Failed to fetch reference details:", error);
    } finally {
      setIsFetchingDetails(false);
    }
  };

  const onSubmit = async (data: ReferenceFormData) => {
    try {
      await addReference(data);
      setIsOpen(false);
    } catch (error) {
      // Error handled by mutation hook
    }
  };

  const canEdit = !readOnly && user?.role === "RESEARCHER";

  return (
    <Card className="border-slate-200 shadow-sm mt-6">
      <CardHeader className="bg-slate-50/50 border-b border-slate-100 flex flex-row items-center justify-between py-4">
        <div>
          <CardTitle className="text-lg flex items-center gap-2">
            <Quote className="w-5 h-5 text-slate-500" />
            References
          </CardTitle>
          <CardDescription>
            Citations and references used in this publication
          </CardDescription>
        </div>
        {canEdit && (
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm" className="bg-white">
                <Plus className="w-4 h-4 mr-2" />
                Add Reference
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Add Reference</DialogTitle>
                <DialogDescription>
                  Search the catalog to auto-fill details, or manually enter the citation.
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-6 pt-4">
                {/* Catalog Search */}
                <div className="relative">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                    <Input
                      placeholder="Search internal catalog (type at least 3 characters)..."
                      className="pl-9"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                    {isSearching && (
                      <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-slate-400" />
                    )}
                  </div>

                  {/* Search Results Dropdown */}
                  {searchQuery.length >= 3 && searchResults && searchResults.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-white rounded-md border border-slate-200 shadow-lg overflow-hidden max-h-60 overflow-y-auto">
                      {searchResults.map((result) => (
                        <button
                          key={result.id}
                          className="w-full text-left px-4 py-3 hover:bg-slate-50 border-b border-slate-100 last:border-0 transition-colors"
                          onClick={() => handleSelectSearchResult(result.id)}
                          disabled={isFetchingDetails}
                        >
                          <div className="font-medium text-sm text-slate-900 line-clamp-1">{result.title}</div>
                          <div className="text-xs text-slate-500 mt-1 flex items-center gap-2">
                            <span className="px-1.5 py-0.5 bg-slate-100 rounded text-slate-600 font-medium">
                              {result.publication_type}
                            </span>
                            {result.doi && <span>DOI: {result.doi}</span>}
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                  {searchQuery.length >= 3 && searchResults?.length === 0 && !isSearching && (
                    <div className="absolute z-10 w-full mt-1 bg-white rounded-md border border-slate-200 shadow-lg p-4 text-sm text-center text-slate-500">
                      No matching publications found.
                    </div>
                  )}
                </div>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-slate-200" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-white px-2 text-slate-500">Manual Entry</span>
                  </div>
                </div>

                <Form {...form}>
                  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <FormField
                      control={form.control}
                      name="title"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Title *</FormLabel>
                          <FormControl>
                            <Input placeholder="Publication title" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="grid grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="authors"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Authors *</FormLabel>
                            <FormControl>
                              <Input placeholder="e.g. Smith J., Doe A." {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="year"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Year *</FormLabel>
                            <FormControl>
                              <Input 
                                type="number" 
                                {...field} 
                                onChange={(e) => field.onChange(parseInt(e.target.value, 10))} 
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    <FormField
                      control={form.control}
                      name="publication_name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Published In (Journal/Conference Name)</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g. Nature, IEEE" {...field} value={field.value || ""} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="grid grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="doi"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>DOI</FormLabel>
                            <FormControl>
                              <Input placeholder="10.1000/xyz123" {...field} value={field.value || ""} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="url"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>URL</FormLabel>
                            <FormControl>
                              <Input placeholder="https://..." {...field} value={field.value || ""} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    <div className="flex justify-end pt-4">
                      <Button type="submit" disabled={isAdding || isFetchingDetails} className="bg-emerald-600 hover:bg-emerald-700">
                        {isAdding ? "Saving..." : "Save Reference"}
                      </Button>
                    </div>
                  </form>
                </Form>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </CardHeader>
      
      <CardContent className="p-0">
        {isLoading ? (
          <div className="p-6 space-y-4">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
        ) : references && references.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {references.sort((a, b) => a.reference_order - b.reference_order).map((ref, idx) => (
              <div key={ref.id} className="p-4 sm:p-6 hover:bg-slate-50 transition-colors flex items-start gap-4 group">
                <div className="flex-shrink-0 w-8 h-8 bg-slate-100 text-slate-500 rounded-full flex items-center justify-center font-medium text-sm">
                  {idx + 1}
                </div>
                <div className="flex-1 min-w-0 space-y-1">
                  <h4 className="text-sm font-medium text-slate-900 leading-snug">
                    {ref.title}
                  </h4>
                  <div className="text-sm text-slate-600 flex flex-wrap items-center gap-x-3 gap-y-1">
                    <span className="flex items-center gap-1">
                      <User className="w-3.5 h-3.5 text-slate-400" />
                      {ref.authors}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      {ref.year}
                    </span>
                    {ref.publication_name && (
                      <span className="flex items-center gap-1">
                        <BookOpen className="w-3.5 h-3.5 text-slate-400" />
                        {ref.publication_name}
                      </span>
                    )}
                  </div>
                  {(ref.doi || ref.url) && (
                    <div className="text-xs text-slate-500 flex items-center gap-3 mt-1.5">
                      {ref.doi && (
                        <span className="flex items-center gap-1">
                          <Tag className="w-3 h-3 text-slate-400" />
                          <a href={`https://doi.org/${ref.doi}`} target="_blank" rel="noreferrer" className="hover:text-blue-600 hover:underline">
                            {ref.doi}
                          </a>
                        </span>
                      )}
                      {ref.url && (
                        <span className="flex items-center gap-1">
                          <LinkIcon className="w-3 h-3 text-slate-400" />
                          <a href={ref.url} target="_blank" rel="noreferrer" className="hover:text-blue-600 hover:underline truncate max-w-[200px]">
                            {ref.url}
                          </a>
                        </span>
                      )}
                    </div>
                  )}
                </div>
                
                {canEdit && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-red-600 transition-all shrink-0"
                    onClick={() => {
                      if (window.confirm("Remove this reference?")) {
                        deleteReference(ref.id);
                      }
                    }}
                    disabled={isDeleting}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center">
            <Quote className="h-10 w-10 mx-auto text-slate-200 mb-3" />
            <p className="text-sm text-slate-500">No references added yet.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
