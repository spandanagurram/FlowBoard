import Card from "../../../components/ui/Card";
import { Link } from "react-router-dom";
import Button from "../../../components/ui/Button";

export default function TaskCard({ task, onCreateSubtask }) {
  return (
    <Card>
      <Link
        to={`/tasks/${task.id}`}
        className="block rounded-xl bg-white p-5 shadow-sm transition hover:shadow-md"
      >
        <div className="space-y-2">

          <div className="text-sm text-gray-500">
            {task.task_number}
          </div>

          <h3 className="text-lg font-semibold">
            {task.title}
          </h3>

          {task.description && (
            <p className="text-gray-600">
              {task.description}
            </p>
          )}

          <div className="flex gap-4 text-sm">

            <span>
              Status: <strong>{task.status}</strong>
            </span>

            <span>
              Priority: <strong>{task.priority}</strong>
            </span>

          </div>

        </div>
      </Link>

      {onCreateSubtask && (
        <div className="mt-4">
          <Button
            className="w-auto"
            onClick={() => onCreateSubtask(task)}
          >
            + New Subtask
          </Button>
        </div>
      )}
    </Card>
  );
}
