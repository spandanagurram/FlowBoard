import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import DashboardLayout from "../../../layouts/DashboardLayout";
import Button from "../../../components/ui/Button";
import {
  deleteWorkspace,
  getWorkspace,
  updateWorkspace,
} from "../../../api/workspace";
import CreateWorkspaceModal from "../components/CreateWorkspaceModal";
import { getProjects } from "../../../api/project";
import ProjectCard from "../../project/components/ProjectCard";
import { Plus } from "lucide-react";
import { useMemo } from "react";
import CreateProjectModal from "../../project/components/CreateProjectModal";
import { createProject } from "../../../api/project";
import { getErrorMessage } from "../../../utils/error";


function WorkspaceDetails() {
  const { workspaceId } = useParams();
  const navigate = useNavigate();

  const [workspace, setWorkspace] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditOpen, setIsEditOpen] = useState(false);

  const [projects, setProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);

  useEffect(() => {
    fetchWorkspace();
    fetchProjects();
  }, [workspaceId]);

  const fetchWorkspace = async () => {
    try {
      setLoading(true);      
      const data = await getWorkspace(workspaceId);
      setWorkspace(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateWorkspace = async (data) => {
    try {
        const updated = await updateWorkspace(workspaceId, data);

        setWorkspace(updated);

        setIsEditOpen(false);
    } catch (error) {
        console.error(error);
        alert(getErrorMessage(error));
    }
 };

  const handleDelete = async () => {
    if (!window.confirm("Delete this workspace?")) return;

    try {
      await deleteWorkspace(workspaceId);
      navigate("/workspaces");
    } catch (error) {
      console.error(error);
      alert(getErrorMessage(error));
    }
  };
 
  const fetchProjects = async () => {
    try {
      setLoadingProjects(true);
      const response = await getProjects(workspaceId);
      setProjects(response.results);
    } catch (error) {
      console.error(error);
    } finally {
      setLoadingProjects(false);
    }
  };

  const workspaceInitialValues = useMemo(
    () => ({
      name: workspace?.name || "",
      description: workspace?.description || "",
    }),
    [workspace?.name, workspace?.description]
  );

  const handleCreateProject = async (data) => {
    try {
      await createProject(workspaceId, data);

      setIsProjectModalOpen(false);

      fetchProjects();
    } catch (error) {
      console.error(error);
      alert(getErrorMessage(error));
    }
  };

  if (loading || !workspace) {
    return (
      <DashboardLayout>
        <p>Loading...</p>
      </DashboardLayout>
    );
  }
  return (
    <DashboardLayout>
      <div className="flex items-start justify-between">

        <div className="space-y-2">
            <h1 className="text-3xl font-bold">
            {workspace.name}
            </h1>

            <p className="text-slate-500">
            {workspace.description || "No description"}
            </p>

            <p className="text-sm text-slate-400">
            Created on{" "}
            {new Date(workspace.created_at).toLocaleDateString()}
            </p>
        </div>

        <div className="flex gap-3">
            <Button
            className="w-auto"
            onClick={() => setIsEditOpen(true)}
            >
            Edit
            </Button>

            <Button
            variant="danger"
            className="w-auto"
            onClick={handleDelete}
            >
            Delete
            </Button>
        </div>

      </div>
      <CreateWorkspaceModal
        isOpen={isEditOpen}
        onClose={() => setIsEditOpen(false)}
        onSubmit={handleUpdateWorkspace}
        initialValues={workspaceInitialValues}
        title="Edit Workspace"
        submitText="Save Changes"
      />
      <div className="mt-10">

        <div className="mb-6 flex items-center justify-between">

            <h2 className="text-2xl font-bold">
            Projects
            </h2>

            <Button
              className="w-auto"
              onClick={() =>
                navigate(
                  `/workspaces/${workspace.id}/members`,
                  {
                    state: {
                      workspaceName: workspace.name,
                    },
                  }
                )
              }
            >
              Members
            </Button>

            <Button
                className="w-auto"
                onClick={() =>
                    navigate(
                        `/workspaces/${workspace.id}/activities`,
                        {
                            state: {
                                workspaceName: workspace.name,
                            },
                        }
                    )
                }
            >
                Activity Logs
            </Button>

            <Button
              className="flex w-auto items-center gap-2"
              onClick={() => setIsProjectModalOpen(true)}
            >
              <Plus size={18} />
              New Project
            </Button>

        </div>

        <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center">

            {loadingProjects ? (
              <p>Loading projects...</p>
            ) : projects.length === 0 ? (
              <p className="text-slate-500">
                No projects yet.
              </p>
            ) : (
              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {projects.map((project) => (
                  <ProjectCard
                    key={project.id}
                    project={project}
                  />
                ))}
              </div>
            )}

        </div>
      </div>
      <CreateProjectModal
        isOpen={isProjectModalOpen}
        onClose={() => setIsProjectModalOpen(false)}
        onSubmit={handleCreateProject}
      />
    </DashboardLayout>
  );
}

export default WorkspaceDetails;