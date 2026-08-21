import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "react-router";
import { institutionRegisterSchema, type InstitutionRegisterFormData } from "@/lib/schemas";
import { useRegisterInstitution } from "@/hooks/useAuthQuery";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FlaskConical, ArrowLeft } from "lucide-react";
import { useState, useRef } from "react";
import { toast } from "sonner";

export default function RegisterInstitution() {
  const registerMutation = useRegisterInstitution();
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const form = useForm<InstitutionRegisterFormData>({
    resolver: zodResolver(institutionRegisterSchema),
    defaultValues: {
      name: "",
      address: "",
      admin_full_name: "",
      admin_email: "",
      admin_password: "",
    },
  });

  function onSubmit(data: InstitutionRegisterFormData) {
    if (!logoFile) {
      toast.error("Please upload an institution logo");
      return;
    }

    registerMutation.mutate({
      ...data,
      logo: logoFile,
    });
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files && e.target.files[0]) {
      setLogoFile(e.target.files[0]);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-4">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-2">
            <FlaskConical className="h-8 w-8 text-emerald-600" />
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">ResearchMesh</h1>
          </div>
          <Link
            to="/login"
            className="flex items-center gap-1 text-sm text-slate-500 hover:text-emerald-600"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Login
          </Link>
        </div>

        <Card className="shadow-lg">
          <CardHeader className="space-y-1">
            <CardTitle className="text-xl font-semibold">Register Your Institution</CardTitle>
            <CardDescription>
              Create an account for your research institution. Admin verification required.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Institution Name</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g., MIT" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="address"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Address</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g., 77 Massachusetts Ave" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="address"
                  render={() => (
                    <FormItem>
                      <FormLabel>Institution Logo</FormLabel>
                      <FormControl>
                        <div>
                          <Input
                            type="file"
                            accept="image/*"
                            ref={fileInputRef}
                            onChange={handleFileChange}
                            className="cursor-pointer"
                          />
                          {logoFile && (
                            <p className="text-xs text-emerald-600 mt-1">
                              Selected: {logoFile.name}
                            </p>
                          )}
                        </div>
                      </FormControl>
                    </FormItem>
                  )}
                />

                <div className="border-t pt-4 mt-4">
                  <h3 className="text-sm font-medium text-slate-900 dark:text-white mb-3">
                    Admin Account Details
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="admin_full_name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Admin Full Name</FormLabel>
                          <FormControl>
                            <Input placeholder="John Smith" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="admin_email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Admin Email</FormLabel>
                          <FormControl>
                            <Input placeholder="admin@university.edu" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="admin_password"
                      render={({ field }) => (
                        <FormItem className="md:col-span-2">
                          <FormLabel>Admin Password</FormLabel>
                          <FormControl>
                            <Input type="password" placeholder="Min 8 characters" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  className="w-full bg-emerald-600 hover:bg-emerald-700"
                  disabled={registerMutation.isPending}
                >
                  {registerMutation.isPending ? "Registering..." : "Register Institution"}
                </Button>
              </form>
            </Form>

            <div className="mt-4 text-center text-sm text-slate-500">
              Already have an account?{" "}
              <Link
                to="/login"
                className="text-emerald-600 hover:text-emerald-700 hover:underline font-medium"
              >
                Sign in
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
