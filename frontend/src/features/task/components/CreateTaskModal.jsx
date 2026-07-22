import { useEffect, useState } from "react";

import Button from "../../../components/ui/Button";
import Input from "../../../components/ui/Input";
import { getWorkspaceMembers } from "../../../api/member";
import { getErrorMessage } from "../../../utils/error";
import Select from "react-select";

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
  workspaceId,
  members: membersProp,
}) {
  const [values, setValues] = useState(initialValues);
  const [members, setMembers] = useState(membersProp || []);
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

  useEffect(() => {
      if (isOpen && !membersProp) {
          fetchMembers();
      }
  }, [isOpen, workspaceId, membersProp]);

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

  const fetchMembers = async () => {
      if (!workspaceId) return;

      try {
          const data = await getWorkspaceMembers(workspaceId);
          setMembers(data.members);
      } catch (error) {
          alert(getErrorMessage(error));
      }
  };


  const memberOptions = members.map((member) => ({
    value: member.user_id,
    label: `${member.username} (${member.role})`,
  }));

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="max-h-[90vh] w-full max-w-md overflow-y-auto rounded-xl bg-white p-6">

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

          <div>
            <label className="mb-1 block text-sm font-medium">
              Assignee
            </label>

            <Select
              options={memberOptions}
              isClearable
              placeholder="Select assignee"
              value={
                memberOptions.find(
                  (option) => option.value === values.assignee
                ) || null
              }
              onChange={(selectedOption) =>
                setValues((current) => ({
                  ...current,
                  assignee: selectedOption ? selectedOption.value : "",
                }))
              }
            />
          </div>

          <Input
            type="date"
            label="Due Date"
            name="due_date"
            value={values.due_date}
            onChange={handleChange}
            min={new Date().toISOString().split("T")[0]}
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