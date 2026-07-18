import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { createPublicationSchema, type CreatePublicationFormData, publicationTypes } from "@/lib/schemas";
import { useCreatePublication } from "@/hooks/usePublicationQuery";
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
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PlusCircle, Loader2 } from "lucide-react";

export function CreatePublicationDialog() {
  const [open, setOpen] = useState(false);
  const { mutateAsync: createPublication, isPending } = useCreatePublication();

  const form = useForm<CreatePublicationFormData>({
    resolver: zodResolver(createPublicationSchema),
    defaultValues: {
      title: "",
      abstract: "",
      publication_type: "JOURNAL",
      doi: "",
    },
  });

  const onSubmit = async (data: CreatePublicationFormData) => {
    const formData = new FormData();
    formData.append("title", data.title);
    formData.append("abstract", data.abstract);
    formData.append("publication_type", data.publication_type);
    if (data.doi) {
      formData.append("doi", data.doi);
    }
    if (data.pdf && data.pdf.length > 0) {
      formData.append("pdf", data.pdf[0]);
    }

    try {
      await createPublication(formData);
      setOpen(false);
      form.reset();
    } catch (error) {
      // Error is handled by the hook via sonner toast
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <PlusCircle className="w-4 h-4 mr-2" />
          Create Publication
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Publication</DialogTitle>
          <DialogDescription>
            Add a new research publication. It will be created as a draft.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Title</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter publication title" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="abstract"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Abstract</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Enter the abstract"
                      className="h-32"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="publication_type"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Publication Type</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a type" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {publicationTypes.map((type) => (
                        <SelectItem key={type} value={type}>
                          {type.replace("_", " ")}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="doi"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>DOI (Optional)</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g., 10.1000/xyz123" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="pdf"
              render={({ field: { value, onChange, ...field } }) => (
                <FormItem>
                  <FormLabel>PDF Document</FormLabel>
                  <FormControl>
                    <Input
                      type="file"
                      accept="application/pdf"
                      onChange={(e) => onChange(e.target.files)}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="flex justify-end pt-4">
              <Button type="submit" disabled={isPending}>
                {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Create Publication
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
