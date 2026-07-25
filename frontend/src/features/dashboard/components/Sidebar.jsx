import {
  LayoutDashboard,
  Briefcase,
  FolderKanban,
  SquareCheckBig,
  LogOut,
} from "lucide-react";

import Logo from "../../../components/common/Logo";
import { NavLink } from "react-router-dom";
import { logout } from "../../../api/auth";

const menuItems = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
    path: "/dashboard",
  },
  {
    label: "Workspaces",
    icon: Briefcase,
    path: "/workspaces",
  },
  {
    label: "Projects",
    icon: FolderKanban,
    path: "/workspaces",
  },
  {
    label: "Tasks",
    icon: SquareCheckBig,
    path: "/workspaces",
  },
];

const handleLogout = async () => {
  await logout();
};

function Sidebar() {
  return (
    <aside className="flex w-60 flex-col border-r border-slate-200 bg-white">

      <div className="border-b border-slate-200 p-6">
        <Logo />
      </div>

      <nav className="flex-1 space-y-2 p-4">
        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.label}
              to={item.path}
              className={({ isActive }) =>
                `flex w-full items-center gap-3 rounded-lg px-4 py-3 transition ${
                  isActive
                    ? "bg-blue-50 text-blue-600 font-semibold"
                    : "text-slate-600 hover:bg-blue-50 hover:text-blue-600"
                }`
              }
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>
      <div className="mt-auto border-t border-slate-200 pt-4">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-slate-600 transition-colors hover:bg-slate-100 hover:text-red-600"
        >
          <LogOut size={18} />
          Logout
        </button>
      </div>

    </aside>
  );
}

export default Sidebar;