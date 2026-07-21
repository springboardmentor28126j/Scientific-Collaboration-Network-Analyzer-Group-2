import { useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router";
import { useAuthStore, useIsSuperAdmin } from "@/stores/authStore";
import { useLogout } from "@/hooks/useAuthQuery";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import {
  FlaskConical,
  LayoutDashboard,
  Building2,
  Users,
  LogOut,
  Menu,
  Shield,
  UserCircle,
  ChevronRight,
  BookOpen,
  ClipboardCheck,
  FileText,
} from "lucide-react";

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  roles: string[];
}

function getNavItems(): NavItem[] {
  return [
    {
      label: "Dashboard",
      path: "/dashboard",
      icon: <LayoutDashboard className="h-5 w-5" />,
      roles: ["SUPER_ADMIN", "INSTITUTION_ADMIN", "RESEARCHER", "REVIEWER"],
    },
    {
      label: "Institutions",
      path: "/dashboard/institutions",
      icon: <Building2 className="h-5 w-5" />,
      roles: ["SUPER_ADMIN"],
    },
    {
      label: "Users",
      path: "/dashboard/users",
      icon: <Users className="h-5 w-5" />,
      roles: ["INSTITUTION_ADMIN"],
    },
    {
      label: "My Research",
      path: "/dashboard/research",
      icon: <BookOpen className="h-5 w-5" />,
      roles: ["RESEARCHER"],
    },
    {
      label: "Publications",
      path: "/dashboard/publications",
      icon: <FileText className="h-5 w-5" />,
      roles: ["SUPER_ADMIN", "INSTITUTION_ADMIN", "RESEARCHER", "REVIEWER"],
    },
    {
      label: "My Reviews",
      path: "/dashboard/reviews",
      icon: <ClipboardCheck className="h-5 w-5" />,
      roles: ["REVIEWER"],
    },
    {
      label: "Profile",
      path: "/dashboard/profile",
      icon: <UserCircle className="h-5 w-5" />,
      roles: ["SUPER_ADMIN", "INSTITUTION_ADMIN", "RESEARCHER", "REVIEWER"],
    },
  ];
}

function SidebarContent() {
  const location = useLocation();
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const isSuperAdmin = useIsSuperAdmin();
  const logoutMutation = useLogout();

  const navItems = getNavItems().filter((item) =>
    item.roles.includes(user?.role || "")
  );

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-6 py-5 border-b">
        <FlaskConical className="h-7 w-7 text-emerald-600" />
        <span className="text-lg font-bold text-slate-900 dark:text-white">
          ResearchMesh
        </span>
      </div>

      <div className="px-4 py-3 border-b">
        <div className="flex items-center gap-3 px-2">
          <div className="w-9 h-9 rounded-full bg-emerald-100 flex items-center justify-center">
            <span className="text-sm font-semibold text-emerald-700">
              {user?.full_name?.charAt(0).toUpperCase() || "U"}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
              {user?.full_name || "User"}
            </p>
            <div className="flex items-center gap-1">
              {isSuperAdmin && <Shield className="h-3 w-3 text-amber-500" />}
              <p className="text-xs text-slate-500 capitalize">{user?.role?.toLowerCase().replace("_", " ")}</p>
            </div>
          </div>
        </div>
      </div>

      <ScrollArea className="flex-1 py-3">
        <nav className="px-3 space-y-1">
          {navItems.map((item) => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                (item.path === "/dashboard"
                  ? location.pathname === item.path
                  : location.pathname.startsWith(item.path))
                  ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200"
              )}
            >
              {item.icon}
              <span className="flex-1 text-left">{item.label}</span>
              {location.pathname === item.path && (
                <ChevronRight className="h-4 w-4" />
              )}
            </button>
          ))}
        </nav>
      </ScrollArea>

      <div className="p-4 border-t">
        <Button
          variant="outline"
          className="w-full justify-start gap-2 text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
          onClick={() => logoutMutation.mutate()}
          disabled={logoutMutation.isPending}
        >
          <LogOut className="h-4 w-4" />
          {logoutMutation.isPending ? "Logging out..." : "Logout"}
        </Button>
      </div>
    </div>
  );
}

export default function DashboardLayout() {
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-slate-900">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex w-64 flex-col fixed inset-y-0 left-0 bg-white dark:bg-slate-800 border-r z-40">
        <SidebarContent />
      </aside>

      {/* Mobile Sidebar */}
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden fixed top-4 left-4 z-50"
          >
            <Menu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="p-0 w-64">
          <SidebarContent />
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <main className="flex-1 lg:ml-64">
        <div className="p-6 lg:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
