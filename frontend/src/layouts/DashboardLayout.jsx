import Sidebar from "../features/dashboard/components/Sidebar";
import TopNavbar from "../features/dashboard/components/TopNavbar";
import { LogOut } from "lucide-react";


function DashboardLayout({ children }) {
  return (
    <div className="flex h-screen bg-slate-100">

      <Sidebar />

      <div className="flex flex-1 flex-col">

        <TopNavbar />


        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>

      </div>

    </div>
  );
}

export default DashboardLayout;