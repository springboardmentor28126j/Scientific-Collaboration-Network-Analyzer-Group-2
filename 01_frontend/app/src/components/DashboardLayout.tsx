import { useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { useAuthStore, useIsSuperAdmin } from "@/stores/authStore";
import { apiClient } from "@/api/client";
import type { SearchResult } from "@/types";
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
  FolderKanban,
  ClipboardCheck,
  Bell,
  CalendarDays,
  FileBarChart,
  Search,
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
      label: "Researchers",
      path: "/dashboard/researchers",
      icon: <Users className="h-5 w-5" />,
      roles: ["SUPER_ADMIN"],
    },
    {
      label: "Users",
      path: "/dashboard/users",
      icon: <Users className="h-5 w-5" />,
      roles: ["INSTITUTION_ADMIN"],
    },
    { label: "Departments", path: "/dashboard/departments", icon: <Building2 className="h-5 w-5" />, roles: ["INSTITUTION_ADMIN"] },
    {
      label: "My Research",
      path: "/dashboard/research",
      icon: <BookOpen className="h-5 w-5" />,
      roles: ["RESEARCHER"],
    },
    {
      label: "Research Hub",
      path: "/dashboard/research-management",
      icon: <FolderKanban className="h-5 w-5" />,
      roles: ["INSTITUTION_ADMIN", "RESEARCHER", "REVIEWER"],
    },
    {
      label: "Publications",
      path: "/dashboard/publications",
      icon: <BookOpen className="h-5 w-5" />,
      roles: ["INSTITUTION_ADMIN", "RESEARCHER"],
    },
    { label: "Conferences", path: "/dashboard/conferences", icon: <CalendarDays className="h-5 w-5" />, roles: ["INSTITUTION_ADMIN", "RESEARCHER", "REVIEWER"] },
    { label: "Projects", path: "/dashboard/projects", icon: <FolderKanban className="h-5 w-5" />, roles: ["INSTITUTION_ADMIN", "RESEARCHER"] },
    { label: "Collaborations", path: "/dashboard/collaborations", icon: <Users className="h-5 w-5" />, roles: ["INSTITUTION_ADMIN", "RESEARCHER"] },
    { label: "Co-authors", path: "/dashboard/coauthors", icon: <Users className="h-5 w-5" />, roles: ["INSTITUTION_ADMIN", "RESEARCHER"] },
    { label: "Citations", path: "/dashboard/citations", icon: <BookOpen className="h-5 w-5" />, roles: ["INSTITUTION_ADMIN", "RESEARCHER"] },
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
    {
      label: "Reports",
      path: "/dashboard/reports",
      icon: <FileBarChart className="h-5 w-5" />,
      roles: ["INSTITUTION_ADMIN", "RESEARCHER", "REVIEWER"],
    },
    {
      label: "Notifications",
      path: "/dashboard/notifications",
      icon: <Bell className="h-5 w-5" />,
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
      <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-800/80">
        <div className="grid h-9 w-9 place-items-center rounded-xl bg-teal-400 text-slate-950 shadow-lg shadow-teal-950/30">
          <FlaskConical className="h-5 w-5" />
        </div>
        <span className="text-lg font-semibold tracking-tight text-white">
          ResearchMesh
        </span>
      </div>

      <div className="px-4 py-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3 px-2">
          <div className="grid h-10 w-10 place-items-center rounded-full bg-gradient-to-br from-teal-300 to-cyan-500 ring-2 ring-slate-700">
            <span className="text-sm font-bold text-slate-950">
              {user?.full_name?.charAt(0).toUpperCase() || "U"}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">
              {user?.full_name || "User"}
            </p>
            <div className="flex items-center gap-1">
              {isSuperAdmin && <Shield className="h-3 w-3 text-amber-300" />}
              <p className="text-[11px] text-slate-400 capitalize">{user?.role?.toLowerCase().replace("_", " ")}</p>
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
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all",
                location.pathname === item.path
                  ? "bg-teal-400 text-slate-950 shadow-lg shadow-teal-950/25"
                  : "text-slate-400 hover:bg-slate-800 hover:text-white"
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

      <div className="p-4 border-t border-slate-800/80">
        <Button
          variant="outline"
          className="w-full justify-start gap-2 border-slate-700 bg-transparent text-slate-300 hover:border-rose-400/40 hover:bg-rose-400/10 hover:text-rose-300"
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
  const [searchQuery, setSearchQuery] = useState("");
  const [searchType, setSearchType] = useState<"All" | SearchResult["type"]>("All");
  const navigate = useNavigate();
  const normalizedSearch = searchQuery.trim();
  const searchResults = useQuery({
    queryKey: ["global-search", normalizedSearch],
    queryFn: () => apiClient.globalSearch(normalizedSearch),
    enabled: normalizedSearch.length >= 2,
  });

  const selectSearchResult = (path: string) => {
    setSearchQuery("");
    navigate(path);
  };
  const filteredSearchResults = searchResults.data?.filter((result) => searchType === "All" || result.type === searchType) ?? [];

  return (
    <div className="flex h-screen overflow-hidden bg-[#f6f8fa] text-slate-900">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex w-64 flex-col fixed inset-y-0 left-0 bg-[#102a35] z-40">
        <SidebarContent />
      </aside>

      {/* Mobile Sidebar */}
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden fixed top-4 left-4 z-50 bg-white shadow-md"
          >
            <Menu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-64 border-none bg-[#102a35] p-0 text-white">
          <SidebarContent />
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <main className="h-screen flex-1 overflow-y-auto lg:ml-64">
        <header className="hidden h-[73px] items-center justify-between border-b border-slate-200 bg-white px-8 lg:flex">
          <div className="relative flex w-full max-w-xl gap-2">
            <div className="relative min-w-0 flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              aria-label="Search"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Search publications, people, projects..."
              className="h-10 w-full rounded-xl border border-slate-200 bg-slate-50 pl-10 pr-4 text-sm outline-none transition focus:border-teal-500 focus:bg-white focus:ring-4 focus:ring-teal-100"
            />
            {normalizedSearch.length >= 2 && (
              <div className="absolute top-12 z-50 w-full overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl">
                {searchResults.isFetching ? <p className="p-4 text-sm text-slate-500">Searching...</p> : filteredSearchResults.length ? filteredSearchResults.map((result) => (
                  <button key={`${result.type}-${result.id}`} onClick={() => selectSearchResult(result.path)} className="block w-full border-b border-slate-100 px-4 py-3 text-left last:border-0 hover:bg-teal-50">
                    <p className="truncate text-sm font-medium text-slate-900">{result.title}</p>
                    <p className="mt-0.5 truncate text-xs text-slate-500">{result.type} · {result.subtitle}</p>
                  </button>
                )) : <p className="p-4 text-sm text-slate-500">No matching records.</p>}
              </div>
            )}
            </div>
            <select aria-label="Search category" value={searchType} onChange={(event) => setSearchType(event.target.value as "All" | SearchResult["type"])} className="h-10 rounded-xl border border-slate-200 bg-slate-50 px-2 text-sm text-slate-600 outline-none focus:border-teal-500">
              <option value="All">All</option>
              <option value="Publication">Publications</option>
              <option value="Researcher">Researchers</option>
              <option value="Conference">Conferences</option>
              <option value="Institution">Institutions</option>
              <option value="Project">Projects</option>
            </select>
          </div>
          <div className="flex items-center gap-4">
            <p className="text-sm text-slate-500">Research management workspace</p>
            <Button variant="ghost" size="icon" className="rounded-xl text-slate-500 hover:bg-slate-100">
              <Bell className="h-5 w-5" />
            </Button>
          </div>
        </header>
        <div className="mx-auto max-w-7xl p-6 pt-20 lg:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
