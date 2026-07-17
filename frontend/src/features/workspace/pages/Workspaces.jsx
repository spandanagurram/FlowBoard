import { useEffect, useState } from "react";

import DashboardLayout from "../../../layouts/DashboardLayout";
import { getWorkspaces } from "../../../api/workspace";
import CreateWorkspaceModal from "../components/CreateWorkspaceModal";
import { createWorkspace } from "../../../api/workspace";
import WorkspaceCard from "../components/WorkspaceCard";
import { getErrorMessage } from "../../../utils/error";


function Workspaces() {
  const [workspaces, setWorkspaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    async function fetchWorkspaces() {
      try {
        const response = await getWorkspaces();
        setWorkspaces(response.results);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    fetchWorkspaces();
  }, []);

  const fetchWorkspaces = async () => {
  try {
    setLoading(true);

    const response = await getWorkspaces();

    setWorkspaces(response.results);
  } catch (error) {
    console.error(error);
  } finally {
    setLoading(false);
  }
};

useEffect(() => {
  fetchWorkspaces();
}, []);

const handleCreateWorkspace = async (data) => {
  try {
    await createWorkspace(data);

    setIsModalOpen(false);

    fetchWorkspaces();
  } catch (error) {
    console.error(error);
    alert(getErrorMessage(error));
  }
};

  return (
    <DashboardLayout>
      <div className="space-y-6">

        <div className="flex items-center justify-between">

          <div>
            <h1 className="text-3xl font-bold">
              Workspaces
            </h1>

            <p className="text-slate-500">
              Manage all your workspaces.
            </p>
          </div>

          <button
            onClick={() => setIsModalOpen(true)}
            className="rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
            >
            + Create Workspace
          </button>

        </div>

        {loading ? (
          <p>Loading...</p>
        ) : (
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">

            {workspaces.map((workspace) => (
              <WorkspaceCard
                key={workspace.id}
                workspace={workspace}
              />
            ))}

          </div>
        )}

      </div>
      <CreateWorkspaceModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateWorkspace}
      />
    </DashboardLayout>
  );
}

export default Workspaces;