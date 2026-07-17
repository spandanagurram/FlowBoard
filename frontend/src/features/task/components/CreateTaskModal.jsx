import { useEffect, useState } from "react";

import Button from "../../../components/ui/Button";
import Input from "../../../components/ui/Input";

const defaultValues = {
  title: "",
  description: "",
  status: "TODO",
  priority: "MEDIUM",
  assignee: "",
  due_date: "",
};

function CreateTaskModal({
  isOpen,
  onClose,
  onSubmit,
  initialValues = defaultValues,
  title = "Create Task",
  submitText = "Create",
  isEdit = false,
}) {
  const [values, setValues] = useState(initialValues);

  useEffect(() => {
    setValues(initialValues);
  }, [
    initialValues.title,
    initialValues.description,
    initialValues.status,
    initialValues.priority,
    initialValues.assignee,
    initialValues.due_date,
  ]);

  const handleChange = (event) => {
    setValues((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit(values);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-md rounded-xl bg-white p-6">

        <h2 className="mb-6 text-2xl font-bold">
          {title}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-5">

          <Input
            label="Title"
            name="title"
            value={values.title}
            onChange={handleChange}
            required
          />

          <Input
            label="Description"
            name="description"
            value={values.description}
            onChange={handleChange}
          />

          <div>
            <label className="mb-1 block text-sm font-medium">
              Status
            </label>

            <select
                name="status"
                value={values.status}
                onChange={handleChange}
                disabled={!isEdit}
                className="w-full rounded-lg border px-3 py-2 disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed"
                >
                <option value="TODO">Todo</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="REVIEW">Review</option>
                <option value="DONE">Done</option>
                <option value="REOPENED">Reopened</option>
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">
              Priority
            </label>

            <select
              name="priority"
              value={values.priority}
              onChange={handleChange}
              className="w-full rounded-lg border px-3 py-2"
            >
              <option value="LOW">LOW</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="HIGH">HIGH</option>
            </select>
          </div>

          <Input
            type="date"
            label="Due Date"
            name="due_date"
            value={values.due_date}
            onChange={handleChange}
          />

          <div className="flex justify-end gap-3">

            <Button
              type="button"
              variant="secondary"
              className="w-auto"
              onClick={onClose}
            >
              Cancel
            </Button>

            <Button
              type="submit"
              className="w-auto"
            >
              {submitText}
            </Button>

          </div>

        </form>

      </div>
    </div>
  );
}

export default CreateTaskModal;