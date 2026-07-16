import {
  FolderKanban,
  ClipboardList,
  Users,
  Activity,
} from "lucide-react";

import Card from "../components/ui/Card";
import Logo from "../components/common/Logo";

const features = [
  {
    icon: FolderKanban,
    title: "Workspace Management",
  },
  {
    icon: ClipboardList,
    title: "Project Tracking",
  },
  {
    icon: Users,
    title: "Team Collaboration",
  },
  {
    icon: Activity,
    title: "Activity Timeline",
  },
];

function AuthLayout({ children }) {
  return (
    <main className="min-h-screen bg-slate-100">
      <div className="grid min-h-screen lg:grid-cols-5">
        {/* Left Branding Panel */}
        <section className="hidden lg:flex lg:col-span-2 flex-col justify-between bg-gradient-to-br from-blue-100 via-blue-400 to-blue-50 p-12 text-white">
          <div>
            <Logo size="lg" />

            <div className="mt-14">
              <h1 className="text-4xl font-bold leading-tight">
                Manage work
                <br />
                without chaos.
              </h1>

              <p className="mt-5 text-lg text-blue-100">
                Organize workspaces, projects and tasks in one place.
              </p>
            </div>

            <div className="mt-14 space-y-6">
              {features.map((feature) => {
                const Icon = feature.icon;

                return (
                  <div
                    key={feature.title}
                    className="flex items-center gap-4"
                  >
                    <div className="rounded-lg bg-white/15 p-2">
                      <Icon size={20} />
                    </div>

                    <span className="text-base font-medium">
                      {feature.title}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          <div>
            <p className="text-sm text-blue-100">
              Built with React + Django
            </p>
          </div>
        </section>

        {/* Right Authentication Panel */}
        <section className="flex items-center justify-center p-6 lg:col-span-3">
          <Card className="max-w-md">
            {children}
          </Card>
        </section>
      </div>
    </main>
  );
}

export default AuthLayout;