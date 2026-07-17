import { useEffect, useState } from "react";
import DashboardLayout from "../../../layouts/DashboardLayout";
import { getWorkspaces } from "../../../api/workspace";

function Dashboard() {
  const [workspaceCount, setWorkspaceCount] = useState(0);
  const [workspaces, setWorkspaces] = useState([]);
  useEffect(() => {
    async function fetchWorkspaces() {
      try {
        const response = await getWorkspaces();

        setWorkspaceCount(response.count);
        setWorkspaces(response.results);
      } catch (error) {
        console.error(error);
      }
    }

    fetchWorkspaces();
  }, []);
  return (
    <DashboardLayout>
      <div className="space-y-8">

        <section className="grid gap-6 md:grid-cols-3">

          <div className="rounded-xl bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-500">
              Total Workspaces
            </p>

            <h3 className="mt-2 text-3xl font-bold">
              {workspaceCount}
            </h3>
          </div>

          <div className="rounded-xl bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-500">
              Total Projects
            </p>

            <h3 className="mt-2 text-3xl font-bold">
              --
            </h3>
          </div>

          <div className="rounded-xl bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-500">
              Total Tasks
            </p>

            <h3 className="mt-2 text-3xl font-bold">
              --
            </h3>
          </div>

        </section>

        <section className="rounded-xl bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold">
            Recent Workspaces
          </h2>

          <p className="mt-4 text-slate-500">
            {workspaces.length === 0 ? (
              <p className="text-slate-500">
                No workspaces found.
              </p>
            ) : (
              <div className="space-y-3">
                {workspaces.map((workspace) => (
                  <div
                    key={workspace.id}
                    className="rounded-lg border border-slate-200 p-4"
                  >
                    <h3 className="font-semibold">
                      {workspace.name}
                    </h3>

                    <p className="text-sm text-slate-500">
                      {workspace.description || "No description"}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </p>
        </section>

      </div>
    </DashboardLayout>
  );
}

export default Dashboard;