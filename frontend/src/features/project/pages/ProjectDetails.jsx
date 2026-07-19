import DashboardLayout from "../../../layouts/DashboardLayout";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../../../components/ui/Button";
import { getErrorMessage } from "../../../utils/error";
import {
  deleteProject,
  getProject,
  updateProject,
} from "../../../api/project";
import CreateProjectModal from "../components/CreateProjectModal";
import { getTasks, createTask } from "../../../api/task";
import TaskCard from "../../task/components/TaskCard";
import CreateTaskModal from "../../task/components/CreateTaskModal";


function ProjectDetails() {
  const { workspaceId, projectId } = useParams();
  const navigate = useNavigate();

  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [tasks, setTasks] = useState([]);
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);


  const fetchProject = async () => {
    try {
        setLoading(true);

        const data = await getProject(projectId);

        setProject(data);
        await fetchTasks();
    } catch (error) {
        console.error(error);
    } finally {
        setLoading(false);
    }
  };

  useEffect(() => {
    fetchProject();
  }, [projectId]);

  const handleUpdateProject = async (values) => {
    try {
        await updateProject(project.id, {
        name: values.name,
        description: values.description,
        });

        setIsEditModalOpen(false);

        const updatedProject = await getProject(project.id);
        setProject(updatedProject);

        alert("Project updated successfully.");
    } catch (error) {
        console.error(error);
        alert(getErrorMessage(error));
    }
 };

  const handleDelete = async () => {
    if (!window.confirm("Delete this project?")) return;

    try {
        await deleteProject(projectId);

        navigate(-1);
    } catch (error) {
        console.error(error);
        alert(getErrorMessage(error));
    }
  };

  const projectInitialValues = useMemo(
    () => ({
        name: project?.name || "",
        key: project?.key || "",
        description: project?.description || "",
    }),
    [project?.name, project?.key, project?.description]
  );


  const fetchTasks = async () => {
    try {
      const data = await getTasks(projectId);
      setTasks(data.results ?? data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleCreateTask = async (values) => {
    try {
      const { status, ...taskData } = values;
      console.log(values);
      const payload = {
        ...values,
        assignee: values.assignee || null,
        due_date: values.due_date || null,
      };

      await createTask(project.id, payload);

      setIsTaskModalOpen(false);

      await fetchTasks();

      alert("Task created successfully.");
    } catch (error) {
      console.error(error);
      console.error(error.response?.data);
      alert(getErrorMessage(error));
    }
  };

  if (loading || !project) {
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
            {project.name}
            </h1>

            <p className="text-slate-500">
            {project.description || "No description"}
            </p>

            <p className="text-sm text-slate-400">
            Key: {project.key}
            </p>

            <p className="text-sm text-slate-400">
            Created on{" "}
            {new Date(project.created_at).toLocaleDateString()}
            </p>

        </div>

        <div className="flex gap-3">

            <Button
            className="w-auto"
            onClick={() => setIsEditModalOpen(true)}
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
      <CreateProjectModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        onSubmit={handleUpdateProject}
        initialValues={projectInitialValues}
        title="Edit Project"
        submitText="Save Changes"
        showKey={false}
      />
      <CreateTaskModal
        isOpen={isTaskModalOpen}
        onClose={() => setIsTaskModalOpen(false)}
        onSubmit={handleCreateTask}
        workspaceId={project.workspace}
      />
      <div className="mt-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold">Tasks</h2>

          <Button
            onClick={() => setIsTaskModalOpen(true)}
            className="w-auto"
          >
            + New Task
          </Button>
        </div>

        {tasks.length === 0 ? (
          <p className="text-gray-500">
            No tasks found.
          </p>
        ) : (
          <div className="grid gap-4">
            {tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
              />
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

export default ProjectDetails;