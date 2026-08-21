import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "react-router";
import { loginSchema, type LoginFormData } from "@/lib/schemas";
import { useLogin } from "@/hooks/useAuthQuery";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowRight, FlaskConical, ShieldCheck, Sparkles } from "lucide-react";

export default function Login() {
  const loginMutation = useLogin();
  const [clearAfterLogout] = useState(() => sessionStorage.getItem("clear-login-form") === "true");
  const [allowAutofill, setAllowAutofill] = useState(true);

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  useEffect(() => {
    if (clearAfterLogout) {
      form.reset({ email: "", password: "" });
      sessionStorage.removeItem("clear-login-form");
    }
  }, [clearAfterLogout, form]);

  function onSubmit(data: LoginFormData) {
    loginMutation.mutate({ username: data.email, password: data.password });
  }

  return (
    <div className="min-h-screen bg-[#eef4f3] p-4 lg:grid lg:grid-cols-2 lg:p-0">
      <section className="relative hidden overflow-hidden bg-[#102a35] p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="absolute -left-32 top-20 h-80 w-80 rounded-full bg-teal-400/15 blur-3xl" />
        <div className="absolute -bottom-32 right-0 h-96 w-96 rounded-full bg-sky-400/10 blur-3xl" />
        <div className="relative flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-teal-400 text-slate-950"><FlaskConical className="h-5 w-5" /></div>
          <span className="text-xl font-semibold tracking-tight">ResearchMesh</span>
        </div>
        <div className="relative max-w-lg">
          <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-teal-300/20 bg-teal-300/10 px-3 py-1.5 text-xs font-medium text-teal-200">
            <Sparkles className="h-3.5 w-3.5" /> Research, made connected
          </div>
          <h1 className="text-5xl font-semibold leading-[1.08] tracking-tight">Bring every research team into focus.</h1>
          <p className="mt-6 max-w-md text-lg leading-8 text-slate-300">Manage institutions, collaborators, and access from one calm, secure workspace.</p>
        </div>
        <div className="relative flex items-center gap-3 text-sm text-slate-300">
          <ShieldCheck className="h-5 w-5 text-teal-300" />
          Role-based access for every member of your institution.
        </div>
      </section>

      <section className="flex min-h-[calc(100vh-2rem)] items-center justify-center lg:min-h-screen lg:p-12">
        <div className="w-full max-w-md">
          <div className="mb-10 flex items-center gap-3 lg:hidden">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-[#102a35] text-teal-300"><FlaskConical className="h-5 w-5" /></div>
            <span className="text-xl font-semibold tracking-tight text-slate-950">ResearchMesh</span>
          </div>

          <Card className="border-0 bg-transparent shadow-none">
          <CardHeader className="space-y-2 px-0 pt-0">
            <p className="page-eyebrow">Welcome back</p>
            <CardTitle className="text-3xl font-semibold tracking-tight text-slate-950">Sign in to your workspace</CardTitle>
            <CardDescription>
              Use your institution account to continue.
            </CardDescription>
          </CardHeader>
          <CardContent className="px-0 pb-0">
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} autoComplete={allowAutofill && !clearAfterLogout ? "on" : "off"} className="space-y-4">
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input className="h-11 border-slate-200 bg-white focus-visible:ring-teal-500"
                          type="email"
                          autoComplete={allowAutofill && !clearAfterLogout ? "username" : "off"}
                          placeholder="admin@university.edu"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Password</FormLabel>
                      <FormControl>
                        <Input className="h-11 border-slate-200 bg-white focus-visible:ring-teal-500"
                          type="password"
                          autoComplete={allowAutofill && !clearAfterLogout ? "current-password" : "new-password"}
                          placeholder="Enter your password"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <label className="flex items-center gap-2 text-sm text-slate-500">
                  <input type="checkbox" checked={allowAutofill} onChange={(event) => setAllowAutofill(event.target.checked)} />
                  Use saved browser credentials
                </label>

                <Button
                  type="submit"
                  className="h-11 w-full bg-[#102a35] text-white hover:bg-[#173c4b]"
                  disabled={loginMutation.isPending}
                >
                  {loginMutation.isPending ? "Signing in..." : <span className="flex items-center gap-2">Sign in <ArrowRight className="h-4 w-4" /></span>}
                </Button>
              </form>
            </Form>

            <div className="mt-4 text-center space-y-2">
              <Link
                to="/forgot-password"
                className="text-sm font-medium text-teal-700 hover:text-teal-800 hover:underline"
              >
                Forgot password?
              </Link>
              <div className="text-sm text-slate-500">
                Want to register your institution?{" "}
                <Link
                  to="/register-institution"
                  className="font-medium text-teal-700 hover:text-teal-800 hover:underline"
                >
                  Register here
                </Link>
              </div>
            </div>
          </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
