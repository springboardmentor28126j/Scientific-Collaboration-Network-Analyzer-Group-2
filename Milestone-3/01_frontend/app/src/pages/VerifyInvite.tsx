import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useSearchParams } from "react-router";
import { verifyInviteSchema, type VerifyInviteFormData } from "@/lib/schemas";
import { useVerifyInvite } from "@/hooks/useAuthQuery";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FlaskConical, XCircle, KeyRound } from "lucide-react";

export default function VerifyInvite() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const verifyMutation = useVerifyInvite();

  const form = useForm<VerifyInviteFormData>({
    resolver: zodResolver(verifyInviteSchema),
    defaultValues: {
      token,
      password: "",
      confirm_password: "",
    },
  });

  function onSubmit(data: VerifyInviteFormData) {
    verifyMutation.mutate({ token: data.token, password: data.password });
  }

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-4">
        <div className="w-full max-w-md text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <XCircle className="h-8 w-8 text-red-600" />
          </div>
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
            Invalid Invite Link
          </h2>
          <p className="text-slate-500 mb-4">
            The invite token is missing or invalid.
          </p>
          <Link to="/login" className="text-emerald-600 hover:text-emerald-700 hover:underline">
            Go to login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-4">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-center gap-2 mb-8">
          <FlaskConical className="h-8 w-8 text-emerald-600" />
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">ResearchMesh</h1>
        </div>

        <Card className="shadow-lg">
          <CardHeader className="space-y-1">
            <div className="flex items-center gap-2 mb-2">
              <KeyRound className="h-5 w-5 text-emerald-600" />
              <CardTitle className="text-xl font-semibold">Set Your Password</CardTitle>
            </div>
            <CardDescription>
              Welcome! Create a password to activate your account.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Password</FormLabel>
                      <FormControl>
                        <Input
                          type="password"
                          placeholder="Min 8 characters"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="confirm_password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Confirm Password</FormLabel>
                      <FormControl>
                        <Input
                          type="password"
                          placeholder="Repeat password"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button
                  type="submit"
                  className="w-full bg-emerald-600 hover:bg-emerald-700"
                  disabled={verifyMutation.isPending}
                >
                  {verifyMutation.isPending ? "Activating..." : "Activate Account"}
                </Button>
              </form>
            </Form>

            <div className="mt-4 text-center">
              <Link
                to="/login"
                className="text-sm text-slate-500 hover:text-emerald-600"
              >
                Already have an account? Sign in
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
