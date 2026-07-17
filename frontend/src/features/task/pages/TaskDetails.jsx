import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import DashboardLayout from "../../../layouts/DashboardLayout";
import Button from "../../../components/ui/Button";
import CreateTaskModal from "../components/CreateTaskModal";

import { getTask, updateTask, deleteTask } from "../../../api/task";
import { getErrorMessage } from "../../../utils/error";

function TaskDetails() {
  const { taskId } = useParams();
  const navigate = useNavigate();

  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditOpen, setIsEditOpen] = useState(false);

  useEffect(() => {
    fetchTask();
  }, [taskId]);

  const fetchTask = async () => {
    try {
      setLoading(true);

      const data = await getTask(taskId);

      setTask(data);
    } catch (error) {
      console.error(error);
      alert(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const taskInitialValues = useMemo(
    () => ({
      title: task?.title || "",
      description: task?.description || "",
      status: task?.status || "TODO",
      priority: task?.priority || "MEDIUM",
      assignee: task?.assignee || null,
      due_date: task?.due_date || "",
    }),
    [task]
  );

  const handleUpdateTask = async (values) => {
    try {
      console.log("Update Payload:", values);
      const payload = {
        ...values,
        assignee: values.assignee || null,
      };

      const updated = await updateTask(taskId, payload);

      setTask(updated);

      setIsEditOpen(false);
    } catch (error) {
      console.error(error.response?.data);
      alert(getErrorMessage(error));
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Delete this task?")) return;

    try {
      await deleteTask(taskId);

      navigate(-1);
    } catch (error) {
      console.error(error);
      alert(getErrorMessage(error));
    }
  };

  if (loading || !task) {
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
            {task.title}
          </h1>

          <p className="text-slate-500">
            {task.description || "No description"}
          </p>

          <div className="flex gap-2">
            <span className="rounded bg-blue-100 px-3 py-1 text-sm">
              {task.status}
            </span>

            <span className="rounded bg-slate-100 px-3 py-1 text-sm">
              {task.priority}
            </span>
          </div>

          <p className="text-sm text-slate-400">
            Due: {task.due_date || "Not set"}
          </p>

          <p className="text-sm text-slate-400">
            Created on{" "}
            {new Date(task.created_at).toLocaleDateString()}
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

      <CreateTaskModal
        isOpen={isEditOpen}
        onClose={() => setIsEditOpen(false)}
        onSubmit={handleUpdateTask}
        initialValues={taskInitialValues}
        title="Edit Task"
        submitText="Save Changes"
        isEdit={true}
      />
    </DashboardLayout>
  );
}

export default TaskDetails;